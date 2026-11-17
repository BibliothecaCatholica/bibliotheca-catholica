#!/usr/bin/env python3
"""Write unlisted Substack draft preview pages from data/substack-drafts.json.

Each entry (slug, title, body, status) becomes /drafts/<slug>/. The index at /drafts/
lists every entry. This script wipes the drafts/ output directory and rebuilds it, so
deleting an entry removes that page and its index row on the next build. Pages carry
noindex,nofollow, use a plain body layout for select-all paste into Substack, and are
not added to the sitemap, nav, search, or feeds. Called at the end of tools/build_static.py.

To retire a page after the post is confirmed live on Substack: delete that entry from
data/substack-drafts.json and commit. Never remove an entry before confirmation. There
is no automatic RSS or publication check.
"""
import html,re,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'substack-drafts.json'
OUT=ROOT/'drafts'
E=lambda s: html.escape(s, quote=False)

def ga_tag():
    tpl=(ROOT/'index.html').read_text(encoding='utf-8')
    m=re.search(r'<!-- Google tag \(gtag\.js\) -->.*?</script>\n<script>.*?</script>\n',tpl,flags=re.S)
    assert m and tpl.count('googletagmanager.com/gtag/js')==1,'index.html must carry exactly one Google tag right after <head>'
    return m.group(0)

def load():
    import json
    data=json.loads(DATA.read_text(encoding='utf-8'))
    drafts=data['drafts'] if isinstance(data,dict) else data
    seen=set()
    out=[]
    for d in drafts:
        slug=d['slug'];title=d['title'];body=d['body']
        assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug),slug
        assert slug not in seen,slug
        assert title and body
        seen.add(slug)
        out.append(d)
    return out

CSS='''body{font-family:Georgia,"Times New Roman",serif;max-width:40rem;margin:2rem auto;padding:0 1.25rem 3rem;line-height:1.55;color:#222;background:#fff}
h1{font-size:1.75rem;line-height:1.25;margin:0 0 .4rem}
.subtitle{font-size:1.1rem;font-style:italic;margin:0 0 1.5rem;color:#333}
article h2{font-size:1.25rem;margin:1.5rem 0 .6rem}
article h3{font-size:1.1rem;margin:1.25rem 0 .5rem}
article p,article li{margin:.75rem 0}
blockquote{margin:1rem 0;padding:.1rem 0 .1rem 1rem;border-left:3px solid #ccc}
a{color:#1a4a8a}
.drafts-index h1{margin-bottom:1rem}
.drafts-index ul{padding-left:1.2rem}
.drafts-index li{margin:.4rem 0}
'''

def page(ga,title,robots,body_html,extra_style=''):
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n'
        +ga+
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>'+E(title)+'</title>\n'
        '<meta name="robots" content="'+robots+'">\n'
        '<style>'+CSS+extra_style+'</style>\n'
        '</head>\n<body>\n'+body_html+'\n</body>\n</html>\n'
    )

def draft_body(d):
    sub=d.get('subtitle') or ''
    inner='<h1>'+E(d['title'])+'</h1>\n'
    if sub:inner+='<p class="subtitle">'+E(sub)+'</p>\n'
    inner+=d['body']
    return '<article>\n'+inner+'\n</article>'

def index_body(drafts):
    items=[]
    for d in drafts:
        sub=' <span class="subtitle">'+E(d['subtitle'])+'</span>' if d.get('subtitle') else ''
        items.append('<li><a href="/drafts/'+E(d['slug'])+'/">'+E(d['title'])+'</a>'+sub+'</li>')
    return (
        '<div class="drafts-index">\n'
        '<h1>Substack draft previews</h1>\n'
        '<p>Unlisted paste pages for Substack drafts. Not published posts, and not linked from the rest of the site.</p>\n'
        '<ul>\n'+'\n'.join(items)+'\n</ul>\n'
        '</div>'
    )

def build():
    drafts=load()
    ga=ga_tag()
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT/'index.html').write_text(page(ga,'Substack draft previews · Bibliotheca Catholica','noindex,nofollow',index_body(drafts)),encoding='utf-8')
    for d in drafts:
        dest=OUT/d['slug'];dest.mkdir()
        (dest/'index.html').write_text(page(ga,d['title'],'noindex,nofollow',draft_body(d)),encoding='utf-8')
    print(len(drafts),'draft pages at /drafts/')

if __name__=='__main__':
    build()
