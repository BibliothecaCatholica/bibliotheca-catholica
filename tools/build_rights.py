#!/usr/bin/env python3
"""Rights status for every Isidore Index record (v16). See AGENTS.md, "Rights badges", and /rights.

Five statuses. Only the first three may show download or reader buttons:
  public_domain_us    Public domain (US): needs written evidence (never a "likely hostable" lead on its own)
  open_license        Open license: CC BY / BY-SA / BY-NC / BY-ND / CC0, with the license link
  permission_granted  Permission granted: a letter on file, with its date
  link_only           Link only: we link to the record's book page on isidore.co, never to its files
  unknown             Unknown: link only until a person reviews it

Two modes:
  python3 tools/build_rights.py --research DIR
      Re-derive data/rights.json from DIR/hosting-classification.csv (research for 6,633 records,
      2026-10-25) and data/library.json. Conservative: every "likely hostable" lead becomes
      `unknown`; the only automatic `public_domain_us` is a record whose source identifier is the
      same Project Gutenberg ebook as a text hosted in our reading room (rights checked under the
      pre-1931 rule). Hand-checked decisions go in MANUAL below, each with evidence and a date.
  python3 tools/build_rights.py
      Validate data/rights.json against data/books.json and data/library.json, then write
      data/rights.js (lazy-loaded by app.js with books.js) and the `r` status on each record in
      data/isidore-matches.json/.js (used by the work pages' "Other formats" panel).
Run tools/build_open_data.py afterwards (it adds rights_status, rights_evidence, rights_checked).
This is not legal advice.
"""
import csv,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'data'
CHECKED='2026-10-25'   # date of the research classification and of this mapping
STATUSES={
 'public_domain_us':{'label':'Public domain (US)','hostable':True,'desc':'Published before 1931, or otherwise shown to be in the US public domain, with written evidence. It may not be public domain in your country.'},
 'open_license':{'label':'Open license','hostable':True,'desc':'Released under an open license (Creative Commons or CC0). The license is linked in the evidence and its terms apply.'},
 'permission_granted':{'label':'Permission granted','hostable':True,'desc':'The rights holder gave written permission. The date of the permission is in the evidence.'},
 'link_only':{'label':'Link only','hostable':False,'desc':'In copyright or restricted. We link to the record’s book page on isidore.co, never to its files.'},
 'unknown':{'label':'Unknown','hostable':False,'desc':'Not yet reviewed, or the evidence is not strong enough. Treated as link only until a person checks it.'},
}
HOSTABLE=[k for k,v in STATUSES.items() if v['hostable']]
LEAD='Lead, not confirmed: '
# research reason code -> (our short code, status, evidence text). Wording is ours, from the research guide.
CODES={
 'H1_PUB_PRE1931':('H1','unknown',LEAD+'the catalog year is before 1931 and there is no ISBN, so the file may be a scan of a pre-1931 printing. The title page has not been checked, and catalog years are often scan or reprint dates.'),
 'H2_PD_SOURCE':('H2','unknown',LEAD+'the catalog’s source identifier points to a public-domain source (Project Gutenberg). Nobody has yet confirmed that this file is that text.'),
 'H3_US_GOV':('H3','unknown',LEAD+'the publisher looks like a US federal agency (17 USC 105). Nobody has yet confirmed that federal employees prepared the work.'),
 'U1a_1931_63_US_NO_RENEWAL_FOUND':('U1a','unknown',LEAD+'a 1931–63 catalog year and a US-looking publisher, with no renewal found by an automated match. That match has limited recall; a manual renewal search and an edition check are needed.'),
 'U1b_1931_63_FOREIGN_OR_UNKNOWN_PUB':('U1b','unknown','A 1931–63 catalog year with a foreign or unknown publisher. Foreign works were restored by the URAA (17 USC 104A) unless public domain at home on 1 January 1996.'),
 'U1c_1931_63_ISBN_REPRINT':('U1c','unknown','A 1931–63 catalog year, but the file has an ISBN, so it is probably a later reprint. Which edition was scanned is not known.'),
 'U2_NO_YEAR':('U2','unknown','No publication year and no usable author dates.'),
 'U2a_NO_YEAR_OLD_AUTHOR':('U2a','unknown','No publication year. The author died before 1931, but the edition or translation has not been checked.'),
 'U3_COMPOSITION_DATE_ONLY':('U3','unknown','The catalog year is the date the work was written, not the date of this edition. The edition or translation could be old (free) or modern (protected).'),
 'U4_MODERN_EDITION_OLD_AUTHOR':('U4','unknown','The author died before 1931, but this is a 1964 or later edition, which may carry a copyrighted translation, edition, or notes.'),
 'L1_PUB_1978_PLUS':('L1','link_only','Catalog year 1978 or later: presumed in copyright unless openly licensed or permission is given. (Catalog years are sometimes digital release dates; ask us to recheck.)'),
 'L2_PUB_1964_1977':('L2','link_only','Catalog year 1964–77: renewal was automatic, so presumed in copyright for 95 years unless published without a notice.'),
 'L3_ISBN_NO_YEAR':('L3','link_only','No year, but the file has an ISBN (a post-1970 edition): presumed in copyright.'),
 'L4_PAPAL_VATICAN_POST1930':('L4','link_only','A papal, curial, conciliar, or bishops’ conference text in a post-1930 or undated edition: rights are reserved by LEV or the USCCB. Read it at the official source.'),
 'L5_RECENT_AUTHOR_NO_YEAR':('L5','link_only','No year, and the author is living or died in 1956 or later: presumed in copyright.'),
 'L6_RENEWED':('L6','link_only','A 1931–63 work with a matching copyright renewal in the NYPL CCE renewals data: protected for 95 years from publication.'),
}
EXTRA_CODES={
 'P1':('public_domain_us','The same Project Gutenberg text as an edition hosted in our reading room, whose rights were checked under the pre-1931 rule:'),
 'M':(None,'Checked by hand:'),  # MANUAL entries carry their own status
}
# Hand-checked decisions: {'<id>': {'status':..., 'evidence':'URL, quote, or CCE volume and page', 'checked':'YYYY-MM-DD', 'checked_by':'name'}}
# Leave empty until a person has checked the title page and the rights evidence (research guide, §1b).
MANUAL={}
def code_table():
    t={c:{'status':s,'text':x} for c,s,x in CODES.values()}
    for c,(s,x) in EXTRA_CODES.items():t[c]={'status':s,'text':x}
    return t
def hosted_pg():
    lib=json.loads((D/'library.json').read_text())
    out={}
    for w in lib['works']:
        for e in w['editions']:
            m=re.fullmatch(r'pg-(\d+)',e['id'])
            if m and e.get('text') and e.get('rights','').startswith('Public domain in the USA'):out[m.group(1)]=(w,e)
    return out
def derive(research):
    rows=list(csv.DictReader(open(Path(research)/'hosting-classification.csv',encoding='utf-8')))
    pg=hosted_pg();rec={}
    for x in rows:
        code,status,_=CODES[x['reason_code']];detail=''
        if code=='H2' or code=='H3':detail='Source: '+x['source_identifier'] if x['source_identifier'] else ''
        if x['renewal_check']:detail=('Automated renewal check: '+x['renewal_check']).rstrip('.')+'.'
        m=re.search(r'gutenberg\.org/(?:ebooks/)?(\d+)',x['source_identifier'] or '')
        # same ebook as a hosted text, and not a modern publisher's ISBN edition that may add its own matter
        if m and m.group(1) in pg and (x['has_isbn']!='True' or re.search(r'gutenberg|public domain books',x['publisher'],re.I)):
            w,e=pg[m.group(1)];code='P1'
            detail='Project Gutenberg #%s, hosted here as “%s” (%s), rights checked %s.'%(m.group(1),w['title'],e['id'],e['checked'])
        rec[x['id']]=[code,detail] if detail else [code]
    for i,m in MANUAL.items():
        assert m['status'] in STATUSES and m.get('evidence') and m.get('checked'),i
        rec[str(i)]=['M',m['evidence'],m['checked'],m['status'],m.get('checked_by','')]
    data={'v':1,'checked':CHECKED,'note':'Rights status of each Isidore Index record. Not legal advice. Built by tools/build_rights.py from research/hosting-classification.csv (2026-10-25); “likely hostable” leads are recorded as unknown until a person checks them.',
          'statuses':STATUSES,'codes':code_table(),'records':dict(sorted(rec.items(),key=lambda kv:int(kv[0])))}
    (D/'rights.json').write_text(json.dumps(data,ensure_ascii=False,indent=0)+'\n')
def status_of(data,r):
    return r[3] if r[0]=='M' else data['codes'][r[0]]['status']
def evidence_of(data,r):
    t=data['codes'][r[0]]['text'];return (t+' '+r[1]).strip() if len(r)>1 and r[1] else t
def checked_of(data,r):
    return r[2] if r[0]=='M' else data['checked']
def validate(data):
    books=json.loads((D/'books.json').read_text())['books'];ids={str(b[0]) for b in books}
    assert set(data['records'])==ids,'rights.json must cover every books.json record'
    pg=hosted_pg()
    for i,r in data['records'].items():
        s=status_of(data,r);assert s in STATUSES,(i,s)
        if STATUSES[s]['hostable']:
            assert r[0] in ('P1','M') and len(r)>1 and len(r[1])>20,'a hostable status needs written evidence: '+i
            assert not evidence_of(data,r).startswith(LEAD),i
        if r[0]=='P1':
            n=re.search(r'Project Gutenberg #(\d+)',r[1]).group(1);assert n in pg,'P1 must point at a hosted, rights-checked edition: '+i
        if r[0].startswith('H') or r[0].startswith('U'):assert s=='unknown',i
        if r[0].startswith('L'):assert s=='link_only',i
    return ids
def main():
    if '--research' in sys.argv:derive(sys.argv[sys.argv.index('--research')+1])
    data=json.loads((D/'rights.json').read_text());validate(data)
    (D/'rights.js').write_text('window.RIGHTS_DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n')
    im=json.loads((D/'isidore-matches.json').read_text())
    for L in im['matches'].values():
        for b in L:b['r']=status_of(data,data['records'][str(b['id'])])
    im['rightsChecked']=data['checked']
    (D/'isidore-matches.json').write_text(json.dumps(im,ensure_ascii=False,indent=1)+'\n')
    (D/'isidore-matches.js').write_text('window.ISIDORE_MATCHES='+json.dumps(im,ensure_ascii=False,separators=(',',':'))+';\n')
    from collections import Counter
    c=Counter(status_of(data,r) for r in data['records'].values())
    sys.path.insert(0,str(ROOT/'tools'));import rights_pages as RP
    pages={'rights':RP.rights_html(STATUSES,c,data['checked']),'takedown':RP.takedown_html()}
    (D/'rights-pages.js').write_text('window.RIGHTS_PAGES='+json.dumps(pages,ensure_ascii=False,separators=(',',':'))+';\n')
    print('rights:',', '.join('%s %d'%(k,c.get(k,0)) for k in STATUSES),'· rights.js',(D/'rights.js').stat().st_size,'bytes')
if __name__=='__main__':main()
