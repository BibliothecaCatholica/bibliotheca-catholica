"""Convert an owner-supplied ZIM into an inert, searchable offline reading copy.
No networking. Outputs are private research artifacts, never public site build inputs.
Install optional requirements with: python3 -m pip install -r tools/saints-archive-requirements.txt
"""
import argparse,hashlib,html,json,re,zipfile
from pathlib import Path
from urllib.parse import urljoin,urlsplit,unquote
from bs4 import BeautifulSoup,Comment
from libzim.reader import Archive
E=html.escape
ALLOWED={'p','br','ul','ol','li','strong','b','em','i','u','ins','blockquote','h2','h3','h4','h5','h6','a','sup','sub','table','tbody','thead','tr','td','th','dl','dt','dd','hr'}
CSS='''body{background:#f6f1e7;color:#27231e;font:18px/1.65 Georgia,serif;max-width:850px;margin:auto;padding:24px}a{color:#7b2033}h1,h2,h3{line-height:1.25}header,aside{border-bottom:1px solid #b3a38d;padding:12px 0}aside,.note{font:15px/1.5 system-ui}input{font:inherit;width:95%;padding:12px}li{margin:.4rem 0}.missing{border-bottom:1px dotted #756c61}table{max-width:100%;display:block;overflow:auto}footer{margin-top:3rem;font-size:15px}'''
def normalize(url):
 u=urlsplit(url);return unquote(u.netloc.lower()+u.path).rstrip('/')+('?' + u.query if u.query else '')
def page(title,body):
 return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; script-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'"><title>'+E(title)+' | CatholicSaints saved reading copy</title><style>'+CSS+'</style><body><header><a href="index.html">Saved reading copy · contents and search</a></header><main>'+body+'</main><footer>Source: CatholicSaints.Info, saved October 25, 2026. Recovered from the supplied partial archive. Source credits remain with their owners. No new reuse license is granted.</footer></body></html>'
def recover(source,out):
 if out.exists():raise ValueError('Choose a new output directory; existing outputs are not overwritten.')
 out.mkdir(parents=True)
 a=Archive(str(source));records=[];mapping={};seen={};html_count=0;skipped=[]
 for e in a.iter_by_path():
  if e.is_redirect:continue
  it=e.get_item()
  if it.mimetype!='text/html' or not e.path.startswith('catholicsaints.info/'):continue
  html_count+=1;s=BeautifulSoup(bytes(it.content),'html.parser');post=s.select_one('.post');content=s.select_one('.postentry')
  if content is None:
   skipped.append({'path':e.path,'reason':'No article body in capture'});continue
  for t in content.select('script,style,iframe,object,embed,form,input,button,svg,math,link,meta,noscript'):t.decompose()
  for c in content.find_all(string=lambda x:isinstance(x,Comment)):c.extract()
  text=content.get_text(' ',strip=True)
  if not text:skipped.append({'path':e.path,'reason':'Empty article body'});continue
  title=(post.select_one('.posttitle').get_text(' ',strip=True) if post and post.select_one('.posttitle') else e.title)
  digest=hashlib.sha256((title+'\n'+text).encode()).hexdigest()
  key=normalize('https://'+e.path)
  if digest in seen:
   mapping[key]=seen[digest]['file'];seen[digest]['aliases'].append('https://'+e.path);continue
  row={'title':title,'source':'https://'+e.path,'file':f'article-{len(records)+1:03}.html','aliases':[],'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'characters':len(text),'content':content}
  seen[digest]=row;records.append(row);mapping[key]=row['file']
 # Redirects can be resolved to a captured article, but missing relative URLs are never guessed.
 for e in a.iter_by_path():
  if e.is_redirect:
   try:
    target=normalize('https://'+e.get_redirect_entry().path)
    if target in mapping:mapping[normalize('https://'+e.path)]=mapping[target]
   except (KeyError,RuntimeError):pass
 missing=set();external=set();images=0;links=0
 for row in records:
  content=row.pop('content');base=row['source']
  for t in list(content.find_all(True)):
   if t.name=='img':
    images+=1;t.replace_with(content.new_string(' [Image omitted: '+(t.get('alt') or 'unlabelled image')+'] ') if hasattr(content,'new_string') and callable(content.new_string) else ' [Image omitted] ');continue
   if t.name not in ALLOWED:t.unwrap();continue
   attrs={}
   if t.name=='a':
    u=urljoin(base,t.get('href',''));p=urlsplit(u)
    if p.scheme in ('http','https'):
     target=mapping.get(normalize(u))
     if target:attrs={'href':target};links+=1
     elif p.netloc.lower()=='catholicsaints.info':attrs={'class':'missing','title':'Not captured in this partial archive: '+u};missing.add(u)
     else:attrs={'href':u,'rel':'noopener noreferrer','title':'Online source; requires internet'};external.add(u)
   t.attrs=attrs
  row['search']=content.get_text(' ',strip=True)
  body='<h1>'+E(row['title'])+'</h1><aside>Partial snapshot · October 25, 2026. This is historical saved content, not a current calendar or cause-status authority. Images are omitted. Dotted terms refer to pages that were not captured. External links require internet.<br>Original address: '+E(base)+'</aside>'+str(content)
  (out/row['file']).write_text(page(row['title'],body))
 payload=[{k:r[k] for k in ('title','file','search')} for r in records]
 data=json.dumps(payload,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
 body='<h1>CatholicSaints.Info · saved reading copy</h1><p>A recovered reading copy of the supplied October 25 archive. <b>This is not a full mirror.</b> Some entries are topic lists or short definitions, rather than saint biographies.</p><p>'+str(len(records))+' distinct captured articles; '+str(html_count)+' HTML entries examined. No live pages were fetched. No claim of permission to republish this collection is made.</p><label for="q">Search titles and saved article text</label><input id="q" type="search" placeholder="Joseph, Bede, patron saints…"><p id="count" role="status"></p><ul id="results">'+''.join('<li><a href="'+r['file']+'">'+E(r['title'])+'</a></li>' for r in records)+'</ul><script>const rows='+data+';const q=document.getElementById("q"),list=document.getElementById("results"),count=document.getElementById("count");function draw(){const terms=q.value.toLocaleLowerCase().trim().split(/\\s+/).filter(Boolean);const hits=rows.filter(r=>terms.every(t=>(r.title+" "+r.search).toLocaleLowerCase().includes(t)));list.replaceChildren();for(const r of hits){const li=document.createElement("li"),a=document.createElement("a");a.href=r.file;a.textContent=r.title;li.append(a);list.append(li)}count.textContent=hits.length+" captured articles"}q.addEventListener("input",draw);draw();</script>'
 (out/'index.html').write_text(page('Contents',body))
 for r in records:r.pop('search')
 report={'source_file':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'captured_date':'2026-10-25','recovered_date':'2026-11-09','archive_entries':a.entry_count,'html_entries':html_count,'distinct_articles':len(records),'duplicate_html_entries':html_count-len(records)-len(skipped),'skipped':skipped,'internal_links_repaired':links,'images_omitted':images,'missing_targets':sorted(missing),'external_targets':sorted(external),'articles':records,'scope':'Private transformation of an owner-supplied partial archive. No new crawl. Not cleared for public republication.'}
 (out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 (out/'README.txt').write_text('Open index.html in a browser after extracting this ZIP. All article text and search work offline. Original capture: 2026-10-25; recovered: 2026-11-09.\nThe companion .zim has a native full-text index for Kiwix.\nThis is a partial saved reading copy, not a newly crawled full website. Source credits are retained. Images, scripts, and uncaptured pages are not supplied. Mixed source rights require review before public reuse.\n')
 archive=out.with_suffix('.zip')
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(out.iterdir()):z.write(p,p.name)
 return report

def write_zim(directory):
 from libzim.writer import Creator,Item,StringProvider,Hint
 class SavedItem(Item):
  def __init__(self,p):super().__init__();self.p=p
  def get_path(self):return self.p.name
  def get_title(self):
   if self.p.suffix=='.html':return BeautifulSoup(self.p.read_text(),'html.parser').title.get_text()
   return self.p.name
  def get_mimetype(self):return 'text/html' if self.p.suffix=='.html' else 'text/plain'
  def get_contentprovider(self):return StringProvider(self.p.read_bytes())
  def get_hints(self):return {Hint.FRONT_ARTICLE:self.p.suffix=='.html'}
 dest=directory.with_suffix('.zim')
 with Creator(str(dest)).config_indexing(True,'eng') as c:
  c.set_mainpath('index.html')
  for key,value in {'Title':'CatholicSaints saved reading copy (partial)','Description':'Recovered October 25, 2026 partial snapshot. Offline text, repaired links, no images.','Language':'eng','Creator':'CatholicSaints.Info (source content)','Publisher':'Personal research copy','Date':'2026-11-09','Name':'catholicsaints-recovered-partial','Tags':'_category:religion;_ftindex:yes'}.items():c.add_metadata(key,value)
  for p in sorted(directory.iterdir()):c.add_item(SavedItem(p))
 return dest
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('--output',required=True,type=Path);args=p.parse_args();report=recover(args.source,args.output);zim=write_zim(args.output);print(json.dumps({k:report[k] for k in ('html_entries','distinct_articles','duplicate_html_entries','internal_links_repaired','images_omitted')}));print(zim)
