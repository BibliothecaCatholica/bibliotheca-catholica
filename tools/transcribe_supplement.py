#!/usr/bin/env python3
"""Transcribe the Supplement to the Third Part of the Summa (English Dominican translation) from Internet Archive OCR.

Network and one-off, like tools/fetch_librivox.py; not part of `npm run build`. Needs `wordfreq` (pip install wordfreq).

Sources (pre-1931 printings of the translation the hosted Parts I to III come from), Internet Archive djvu.xml OCR:
  summatheologi18thom            Third Part, Fourth Number (QQ. 84 to Suppl. 33), Washbourne and Benziger, 1917
  summatheologi19thom            Third Part (Supplement), QQ. 34 to 68, Burns Oates and Washbourne and Benziger, 1922
  summatheologi20thom            Third Part (Supplement), QQ. 69 to 86, Burns Oates and Washbourne, 1921
  summatheologicao0000unse_f4n0  Third Part (Supplement), QQ. 87 to 99 and Appendices, Benziger Brothers, 1922

What the tool does, and nothing more:
  * keeps the page text in reading order and drops running heads, page numbers, and scanning noise outside the text;
  * moves each page's footnotes to just after the paragraph they belong to, as [*...] like the Gutenberg Parts;
  * rejoins words hyphenated at line ends and paragraphs broken by a page turn;
  * fixes a short, fixed list of OCR confusions (see FIXED and confusion()) only when the result is a word the
    Gutenberg Summa itself uses and the OCR form is not, and records every change;
  * writes the headings in the Gutenberg Parts' layout so tools/build_summa.py reads them the same way, and leaves
    out the printed "We proceed thus to the ... Article", which the Gutenberg Parts also omit;
  * flags (never rewrites) any paragraph that still has a word it could not confidently read.
It does not supply missing words. Output: data/texts/ia-summa-supplement.txt, data/sources/ia-summa-supplement.json (sources,
SHA-256 of each OCR file, counts), and data/summa-supplement-ocr.json (corrections and flagged paragraphs).

    python3 tools/transcribe_supplement.py --cache /tmp/supp-ocr
"""
import argparse,collections,hashlib,json,re,sys,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EDITION='ia-summa-supplement'
VOLS=[  # identifier, imprint year, publisher line, questions in this volume, title-page wording
 ('summatheologi18thom',1917,'R. & T. Washbourne, London; Benziger Brothers, New York',(1,33),'Third Part, Fourth Number (QQ. LXXXIV to Suppl. XXXIII)'),
 ('summatheologi19thom',1922,'Burns Oates & Washbourne, London; Benziger Brothers, New York',(34,68),'Third Part (Supplement), QQ. XXXIV to LXVIII'),
 ('summatheologi20thom',1921,'Burns Oates & Washbourne, London',(69,86),'Third Part (Supplement), QQ. LXIX to LXXXVI'),
 ('summatheologicao0000unse_f4n0',1922,'Benziger Brothers, New York',(87,99),'Third Part (Supplement), QQ. LXXXVII to XCIX and Appendices'),
]
# Two pages of summatheologi20thom were scanned curled and their OCR is unreadable; they are taken from another scan of
# the same 1921 printing (imprimatur Aug. 4, 1921), at the same printed pages (67 and 83).
SUBST_ID='summatheologicao0020thom_q5p9'
SUBST={('summatheologi20thom',78):(SUBST_ID,78),('summatheologi20thom',94):(SUBST_ID,94)}
CACHE=None
ROMAN={'I':1,'V':5,'X':10,'L':50,'C':100}
def roman(s):
    s=s.upper();v=0
    if not re.fullmatch(r'C{0,3}(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})',s) or not s:return None
    for k,c in enumerate(s):
        n=ROMAN[c];v+=-n if k+1<len(s) and ROMAN[s[k+1]]>n else n
    return v
ORD='First Second Third Fourth Fifth Sixth Seventh Eighth Ninth Tenth Eleventh Twelfth Thirteenth Fourteenth Fifteenth Sixteenth Seventeenth Eighteenth Nineteenth Twentieth'.split()
NUMW='One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve Thirteen Fourteen Fifteen Sixteen Seventeen Eighteen Nineteen Twenty'.split()
def fetch(vid,cache):
    p=Path(cache)/(vid+'_djvu.xml')
    if not p.exists():
        p.parent.mkdir(parents=True,exist_ok=True)
        req=urllib.request.Request('https://archive.org/download/%s/%s_djvu.xml'%(vid,vid),headers={'User-Agent':'BibliothecaCatholica/1.0 (+https://bibliothecacatholica.com)'})
        with urllib.request.urlopen(req,timeout=300) as r:p.write_bytes(r.read())
    return p
def pages(path):
    out=[]
    for pi,o in enumerate(ET.parse(path).getroot().find('BODY').findall('OBJECT')):
        H=int(o.get('height'));paras=[]
        for para in o.iter('PARAGRAPH'):
            lines=[]
            for ln in para.iter('LINE'):
                ws=[w for w in ln.findall('WORD') if (w.text or '').strip()]
                if not ws:continue
                c=[list(map(int,w.get('coords').split(',')[:4])) for w in ws]
                lines.append(dict(t=' '.join(w.text.strip() for w in ws),x=min(a[0] for a in c),y=max(a[1] for a in c),h=sorted(a[1]-a[3] for a in c)[len(c)//2]))
            if lines:paras.append(lines)
        out.append(dict(i=pi,H=H,p=paras))
    return out
HEAD=re.compile(r"(SUMMA|THEOLOGIC|[QgO]\.\s*\S{1,4}\s*A[rR][tTr]|^\d+\s+[A-Z][A-Z ]{6,})",re.I)
FOOT=re.compile(r'^\s*[\*†‡§¶]\s*\S|^\s*[tf\+]\s+[A-Z]')
NOISE=re.compile(r'^[\W\d_ilIoO]{0,6}$')
class Vocab:
    def __init__(self):
        self.pg=collections.Counter();self.cs=collections.Counter()
        for n in (17611,17897,18755,19950):
            for w in re.findall(r"[A-Za-z]+",(ROOT/('data/texts/pg-%d.txt'%n)).read_text(encoding='utf-8')):self.pg[w.lower()]+=1;self.cs[w]+=1
        from wordfreq import zipf_frequency;self.z=lambda w:zipf_frequency(w,'en')
        self.bi=collections.Counter();self.tri=collections.Counter()
        for n in (17611,17897,18755,19950):
            ws=re.findall(r"[a-z]+",(ROOT/('data/texts/pg-%d.txt'%n)).read_text(encoding='utf-8').lower())
            self.bi.update(zip(ws,ws[1:]));self.tri.update(zip(ws,ws[1:],ws[2:]))
    def known(self,w):
        w=re.sub(r"'s$",'',w).lower()
        if '-' in w:return all(self.known(x) for x in w.split('-') if x)
        return self.pg[w]>0 or self.z(w)>=1.0
CONF=[('Ti','h'),('\\^','y'),('\\n','wi'),('U','li'),('fii','ffi'),('fi','ffi'),('H','fi'),('id','ul'),('4i','h'),('^V','W'),('hv','lw'),('ai','u'),('Ji','h'),('7n','m'),('7i','n'),('\\d','vi'),('\\','v'),('m','in'),('3^','y'),('\\i','v'),('mi','nn'),('3^','y'),('\\\\','w'),('lL','ll'),('IlL','III'),('^v','w'),('^^','w'),('^','y'),('U','ll'),('h','li'),('h','fi'),('h','ll'),('}^','y'),('^',''),('}','y'),('\\v','w'),('im','un'),('J','h'),('m','ni'),('d','i'),('ii','n'),('iu','ni'),('fl','fi'),('&','f'),('h','b'),('b','h'),('li','h'),('ii','u'),('rn','m'),('m','rn'),('c','e'),('e','c'),('l','i'),('i','l'),('j','f'),('f','j'),('1','l'),('l','I'),('I','l'),('0','o'),('o','e'),('n','u'),('u','n'),('v','y'),('t','f'),('f','t'),('&','fi'),('&','ffi'),('&','ff'),('fi','f'),('H','li'),('in','m'),('cl','d'),('d','cl'),('tli','th'),('iu','m'),('S','s'),('5','s')]
def confusion(w,V,loose=False):
    """Candidates one OCR confusion away from w that the Gutenberg Summa uses (counts), best first. When the OCR form
    is no English word at all (loose), an English word the Summa does not happen to use is also accepted."""
    lw=w.lower();cands={}
    for a,b in CONF:
        for m in re.finditer(re.escape(a),w):
            c=w[:m.start()]+b+w[m.end():]
            lc=c.lower()
            if re.search(r'[^A-Za-z]',c) or re.search(r'[a-z][A-Z]',c):continue
            if V.pg[lc]>=3:cands[c]=V.pg[lc]+1000
            elif loose and V.z(lc)>=1.0:cands[c]=V.z(lc)
    return sorted(cands,key=lambda c:-cands[c])
FIXED=[  # (pattern, replacement): label and punctuation forms the OCR misreads the same way every time
 (r'^O[bh]j?[ji]?ection\b',r'Objection'),(r'^(Reply\s+)?O[bh][ij]\s*[.,]\s*-?\s*(?=[\dilxz$^|])',lambda m:(m.group(1) or '')+'Obj. '),
 (r'\bOh[ij]\.',r'Obj.'),(r'\bOb[ij]\b(?!\.)',r'Obj.'),(r'\bObj\s*,',r'Obj.'),(r'^[/|!lI1]\s*ans\S{2,5}\s+th(?:at|ai|a1|al)\b\s*[.,;:y]?\s*(?=[A-Z(])',r'I answer that, '),
 (r'^[O0][a-z0-9]{1,2}\s+the\s+c[o0]ntrary\b',r'On the contrary'),(r'^On\s+the\s+c[o0]ntrary\s*(?:[.,;:]\s*|y\s+)(?=[A-Z(])',r'On the contrary, '),(r'\{In\b',r'(In'),(r'\bArticles?\s*\.\s*\}',lambda m:m.group(0).replace('}',')')),
 (r'[•■►]',r''),(r'(?:(?<=\s)|^)[\^|=~>°_<]+(?=\s|$)',r''),(r'_',r''),(r"(\w)-'?\s+(?=[a-z])",r'\1'),(r'\{',r'('),(r'\bDe(?=[A-Z][a-z])',r'De '),(r'\s+([?:;!,.)\]])',r'\1'),(r'([(\[])\s+',r'\1'),(r'[“”„]',r'"'),(r"[‘’]",r"'"),(r'\s*—\s*',r'--'),(r'\s*–\s*',r'-'),(r'\s{2,}',r' '),(r"''",r'"'),
]
LABEL2=re.compile(r'^(Reply\s+)?([O0][bh0][\W\]jJij7]{0,3}|Objection)\s*[.,\-]*\s*([0-9ilIxz$Z^|]{1,2}|\d+)\s*[.,:\-]+\s+(?=[A-Z])')
LABEL=re.compile(r'^(Objection\s+\S{1,2}[.,:]|Oh?[bh][ij]\.\s*\S{1,2}[.,:]|Reply\s+O\w{1,2}\.|[/|!lI1]\s*answer\s+th|On\s+the\s+contrary)')
WEP=re.compile(r'^\W{0,3}(?:W|IV|\]V|V|\\V)\s*[ec][\s■]+proceed\s+\w+',re.I)
NUM_LABEL=re.compile(r'^(Objection|Obj\.|Reply\s+Obj\.)[,.]?\s*([0-9ilIoOz|x]{1,3}(?:(?:\s*,\s*|\s+and\s+)[0-9ilIoOz|x]{1,2})*)\^?(?:\s*[.,:]\s*|\s+(?=Further|It|The|But|Since|If|Because|Moreover|Again|For|Now|This|Hence))')
def fix_num(s):
    m={'i':'1','l':'1','I':'1','|':'1','o':'0','O':'0','z':'2'};return ''.join(m.get(c,c) for c in s)
def join_lines(lines,V,notes):
    t=''
    for ln in lines:
        s=ln['t'].strip()
        if not t:t=s;continue
        m=re.search(r'(\w+)-$',t)
        if m:
            nxt=re.match(r'([a-z]+)(.*)$',s)
            if nxt:
                a,b=m.group(1),nxt.group(1);joined=a+b
                if V.pg[joined.lower()] or (V.z(joined.lower())>=1.5 and not V.pg[(a+'-'+b).lower()]):t=t[:-1]+s
                elif V.pg[a.lower()] and V.pg[b.lower()] and V.z((a+'-'+b).lower())>0:t=t+s
                else:t=t[:-1]+s
                continue
        t=t+' '+s
    return t
NEVER={'hut':'but','hy':'by','ls':'is','ts':'is','tt':'it','ot':'of','oi':'of','thai':'that','docs':'does','bom':'born','che':'the','arc':'are','ave':'are','ftom':'from','wko':'who','tlie':'the','tbe':'the','ihe':'the','aud':'and','iu':'in','bnt':'but'}
REAL={'hum':('burn',),'bum':('burn',),'fife':('life',),'fixe':('fire',),'mil':('will',),'umbo':('limbo',),'chanty':('charity',),'tiling':('thing',),'modem':('modern',),'sim':('sun',),'hues':('lines',),'une':('line',),'cure':('care',),'lot':('not',),'powder':('power',),'cap':('can',),'he':('be',),'had':('bad',),'hound':('bound',),'lire':('fire',),'m':('in',),'ho':('be',),'tho':('the',),'bo':('be',),'oven':('even',)}
def ctx2(m,ctx):
    class M:
        def __init__(s,m):s.m=m
        def group(s,k=0):return {0:s.m.group(0),1:s.m.group(1),2:s.m.group(2),3:s.m.group(3)}[k]
    return ctx(M(m))
def clean_words(p,V,notes,where):
    def word(m):
        w=m.group(0)
        core=w
        odd=bool(re.search(r'[^A-Za-z]|[a-z][A-Z]|^[A-Z][a-z]*[A-Z]',core))
        if core and (odd or V.pg[core.lower()]==0 and V.z(core.lower())<3):
            c=confusion(core,V,loose=odd or V.z(core.lower())==0)
            if c:notes['fixes'][core+' -> '+c[0]]+=1;return w.replace(core,c[0])
        if core.isalpha() and not V.known(core) and len(core)>4 and core[-1] in 'tf' and V.pg[core[:-1].lower()]>=3:
            notes['fixes']['footnote mark %s -> %s†'%(core,core[:-1])]+=1;return w.replace(core,core[:-1]+'†')
        if core.isalpha() and not V.known(core) and V.z(core.lower())==0 and len(core)>=4:
            for k in range(1,len(core)):
                x,y=core[:k],core[k:]
                if V.pg[x.lower()]>=50 and V.pg[y.lower()]>=50 and V.bi[(x.lower(),y.lower())]>=5:
                    notes['fixes']['run together %s -> %s %s'%(core,x,y)]+=1;return w.replace(core,x+' '+y)
        if not core or V.known(core) or len(core)<3 and core.lower() in ('ad','ib','cf','ff','vv','id'):return w
        if re.fullmatch(r'[IVXLCivxlc]+',core):return w
        c=confusion(core,V)
        if c:
            fixed=w.replace(core,c[0]);notes['fixes'][core+' -> '+c[0]]+=1;return fixed
        return w
    p=re.sub(r"[A-Za-z0-9&\\}^]*[A-Za-z][A-Za-z0-9&\\}^]*",lambda m:m.group(0) if re.fullmatch(r'\d+(st|nd|rd|th|a|b)?|[A-Za-z]+',m.group(0)) and re.search(r'\d',m.group(0)) else word(m),p)
    # misreadings that are never words in this text
    for a,b in NEVER.items():
        n=len(re.findall(r'\b%s\b'%a,p))
        if n:p=re.sub(r'\b%s\b'%a,b,p);notes['fixes'][a+' -> '+b]+=n
    # real words misread as other real words (b/h, f/l): changed only where the Gutenberg Summa has the corrected
    # three-word sequence and never the OCR one
    def ctx(m):
        pre,w,nxt=m.group(1),m.group(2),m.group(3)
        for alt in REAL.get(w,()):
            a,b,c=pre.lower(),w.lower(),nxt.lower()
            alt_s=(V.bi[(a,alt)]+1)*(V.bi[(alt,c)]+1);orig_s=(V.bi[(a,b)]+1)*(V.bi[(b,c)]+1)
            strict=b in ('he',)  # "he" is common in its own right: only where the Summa has the corrected sequence and never the pair
            if V.tri[(a,b,c)]==0 and (V.tri[(a,alt,c)]>=3 and (not strict or V.bi[(a,b)]==0 or V.bi[(b,c)]==0) or not strict and alt_s>=50*orig_s and alt_s>=200):
                notes['fixes']['%s -> %s (context)'%(w,alt)]+=1;return pre+m.group(0)[len(pre):-len(nxt)].replace(w,alt)+nxt
        return m.group(0)
    p=re.sub(r"(?<![A-Za-z])([A-Za-z]+)[ ,]+(%s)[ ,]+([A-Za-z]+)"%'|'.join(REAL),lambda m:ctx2(m,ctx),p)
    return p
def na_words(q,a,cache):
    """Words of one article in New Advent's transcription of the same translation. Used only to clear a flag on a word
    the scan has and New Advent has too (Latin citations, rare English); never to change the text."""
    p=Path(cache)/'newadvent'/('50%02d.htm'%q)
    if not p.exists():
        p.parent.mkdir(parents=True,exist_ok=True)
        req=urllib.request.Request('https://www.newadvent.org/summa/50%02d.htm'%q,headers={'User-Agent':'Mozilla/5.0 (BibliothecaCatholica transcription check)'})
        with urllib.request.urlopen(req,timeout=120) as r:p.write_bytes(r.read())
    import html as H
    parts=re.split(r'<h2 id="article(\d+)">',p.read_text(encoding='latin-1'))
    for k in range(1,len(parts),2):
        if int(parts[k])==a:return set(re.findall(r"[a-z]+",H.unescape(re.sub(r'<.*?>',' ',parts[k+1])).lower()))
    return set()
def suspicious(p,V):
    """Words still unreadable after the fixes: stray symbols, letters mixed with digits or odd capitals, and words that
    are in neither the Gutenberg Summa, an English word list, nor (three or more times) this transcription itself."""
    bad=[]
    for w in re.split(r"\s+|--|\.\.\.",p):
        core=re.sub(r"^[\"'(\[*]+|[\"'.,;:?!)\]*]+$",'',w)
        if not core or re.fullmatch(r"[\d.,:;\-]+|[IVXLCivxlc]+\.?|\d+(st|nd|rd|th)|[a-z]\)|\([a-z0-9]+\)?",core):continue
        if re.search(r"[\^\\{}<>|~@#$%=_°►]|[a-z][A-Z]|[A-Za-z]\d|\d[A-Za-z]",core):bad.append(core);continue
        for part in core.split('-'):
            part=re.sub(r"'s$",'',part)
            if len(part)>=3 and part.isalpha() and part.islower() and not V.known(part) and V.seen[part]<3:bad.append(core);break
    ws=re.findall(r"[A-Za-z]+",p)
    for k in range(1,len(ws)-1):
        if ws[k]=='he':
            a,c=ws[k-1].lower(),ws[k+1].lower()
            if V.tri[(a,'be',c)]>=3 and V.tri[(a,'he',c)]==0:bad.append('he (be?)')
    return bad
def body_lines(pg,med):
    """Body lines and footnote lines of a page, running head and page number removed."""
    flat=[(k,l) for k,para in enumerate(pg['p']) for l in para]
    body,foot=[],[];infoot=False
    for n,(k,l) in enumerate(flat):
        t=l['t'].strip()
        if l['y']<pg['H']*0.11 and (HEAD.search(t) or NOISE.match(t)):continue
        if NOISE.match(t) and (l['y']>pg['H']*0.85 or l['y']<pg['H']*0.11):continue
        if not infoot and l['y']>pg['H']*0.55 and FOOT.match(t) and l['h']<med*0.92:infoot=True
        (foot if infoot else body).append((k,l))
    return body,foot
def build(cache):
    V=Vocab();notes={'fixes':collections.Counter(),'flags':[],'volumes':[]}
    allparas=[]  # (vol, page, text, footnotes)
    sp=fetch(SUBST_ID,cache);SP=pages(sp);sh=[l['h'] for pg in SP for para in pg['p'] for l in para];smed=sorted(sh)[len(sh)//2]
    notes['substitutes']=dict(identifier=SUBST_ID,url='https://archive.org/details/'+SUBST_ID,ocr=SUBST_ID+'_djvu.xml',ocrSha256=hashlib.sha256(sp.read_bytes()).hexdigest(),
        year=1921,publisher='Burns Oates & Washbourne, London',pages=[dict(volume=v,page=a,substitutePage=b) for (v,a),(_,b) in sorted(SUBST.items())])
    for vid,year,pub,(q0,q1),tp in VOLS:
        path=fetch(vid,cache);raw=path.read_bytes()
        notes['volumes'].append(dict(identifier=vid,url='https://archive.org/details/'+vid,ocr=vid+'_djvu.xml',ocrSha256=hashlib.sha256(raw).hexdigest(),year=year,publisher=pub,titlePage=tp,questions=[q0,q1]))
        P=pages(path);hs=[l['h'] for pg in P for para in pg['p'] for l in para];med=sorted(hs)[len(hs)//2]
        # the volume's Supplement text starts at its first "QUESTION <q0>" heading after the contents
        start=None
        for pg in P:
            for para in pg['p']:
                t=re.sub(r'\s+',' ',para[0]['t']).strip().rstrip('.')
                m=re.fullmatch(r'QUESTION ([IVXLCil]+)',t)
                if m and roman(m.group(1).replace('l','I').replace('i','I'))==q0 and len(para)<=2:start=pg['i'];break
            if start is not None:break
        assert start is not None,(vid,'no start')
        if vid=='summatheologi18thom':  # the Supplement begins partway through this volume; skip the Third Part questions
            start=next(pg['i'] for pg in P if pg['i']>=start and any(re.match(r'SUPPLEMENT\s*$',l['t'].strip()) for para in pg['p'] for l in para))
        END=re.compile(r'^(Printed in England|PRINTED IN|ST\.? THOMAS AQUINAS IN ENGLISH|APPENDIX\s+I\b\.?\s*$)',re.I)
        stop=False
        for pg in P[start:]:
            if stop:break
            src=vid
            if (vid,pg['i']) in SUBST:src,k=SUBST[(vid,pg['i'])];body,foot=body_lines(SP[k],smed)
            else:body,foot=body_lines(pg,med)
            groups=[];cur=None
            xs=sorted(l['x'] for k,l in body);left=xs[len(xs)//4] if xs else 0
            for n_,(k,l) in enumerate(body):
                # the OCR sometimes runs two printed paragraphs together: a new one starts at an indented line after a
                # line that ends a sentence, or at an article label
                prev=cur[1][-1]['t'].strip() if cur else ''
                newpara=cur is not None and cur[0]==k and re.search(r'[.?!:"\'”]$',prev) and (l['x']-left>med*0.9 or LABEL.match(l['t'].strip()))
                if cur is None or cur[0]!=k or newpara:cur=[k,[]];groups.append(cur)
                cur[1].append(l)
            texts=[join_lines(g[1],V,notes) for g in groups]
            for j,x in enumerate(texts):
                if END.match(x.strip()):texts=texts[:j];groups=groups[:j];stop=True;notes['volumes'][-1]['endPage']=pg['i'];break
            fn=[]
            for k,l in foot:
                t=l['t'].strip()
                if FOOT.match(t) or not fn:fn.append(t)
                else:fn[-1]=join_lines([{'t':fn[-1]},{'t':t}],V,notes)
            for j,t in enumerate(texts):allparas.append(dict(vol=src,page=pg['i'] if src==vid else SUBST[(vid,pg['i'])][1],t=t,foot=fn if j==len(texts)-1 else [],ind=groups[j][1][0]['x']))
        notes['volumes'][-1]['pages']=[start,len(P)-1]
    # merge paragraphs broken by a page turn or by the OCR: the earlier one does not end a sentence and the later starts in lower case
    merged=[]
    for p in allparas:
        if merged and not re.search(r'[.?!:)"\]]$',merged[-1]['t']) and re.match(r'^[a-z(]',p['t']):
            m=merged[-1];m['t']=join_lines([{'t':m['t']},{'t':p['t']}],V,notes);m['foot']+=p['foot'];m['pages'].append(p['page']);continue
        if merged and re.search(r'\w-$',merged[-1]['t']) and re.match(r'^[a-z]',p['t']):
            m=merged[-1];m['t']=join_lines([{'t':m['t']},{'t':p['t']}],V,notes);m['foot']+=p['foot'];m['pages'].append(p['page']);continue
        p=dict(p);p['pages']=[p['page']];merged.append(p)
    # the OCR sometimes runs an article's title, its "We proceed thus" line, and the first objection into one paragraph
    split=[];rx=re.compile(r'\s*\b((?:W|IV|\]V|V)\s*[ec][\s■]+proceed\s+\w+\s+to\s+(?:the|this)\s+(?:\w+\s+)?Article\s*[:;.]?\s*[—\-:■]*)\s*',re.I)
    for p in merged:
        parts=[x for x in rx.split(p['t']) if x and x.strip()]
        if len(parts)==1:split.append(p);continue
        for k,x in enumerate(parts):split.append(dict(p,t=x.strip(),foot=p['foot'] if k==len(parts)-1 else []))
        notes['fixes']['paragraph split at "We proceed thus"']+=1
    return V,notes,split
def ordinal(w):
    """The ordinal an OCR'd article heading word stands for (Sfxond, S1xtH), or None."""
    w=w.lower().replace('1','i').replace('0','o')
    def d(a,b):
        r=list(range(len(b)+1))
        for x in a:
            nr=[r[0]+1]
            for j,y in enumerate(b):nr.append(min(r[j+1]+1,nr[j]+1,r[j]+(x!=y)))
            r=nr
        return r[-1]
    best=sorted((d(w,o.lower()),o) for o in ORD)
    return best[0][1] if best[0][0]<=(1 if len(w)<=5 else 2) and (len(best)<2 or best[1][0]>best[0][0]) else None
def recase(t,V):
    """Article titles are set in small capitals, which the OCR returns in upper or lower case: give them sentence case,
    capitalizing the words the Gutenberg Summa capitalizes (God, Christ, Augustine)."""
    ws=t.split(' ');out=[]
    for k,w in enumerate(ws):
        m=re.match(r"^([^A-Za-z]*)([A-Za-z']+)(.*)$",w)
        if not m:out.append(w);continue
        a,b,c=m.groups();lw=b.lower()
        if k==0 and lw!='whether' and len(lw)==7 and sum(x!=y for x,y in zip(lw,'whether'))==1:
            lw='whether'  # Vhether, Wliether: the first word of an article title
        cap=lw!='whether' and (V.cs[lw.capitalize()]>V.cs[lw] or b=='I')
        out.append(a+(lw.capitalize() if k==0 or cap else lw)+c)
    return ' '.join(out).replace(' ?','?')
def braces(t):
    """A } closes a parenthesis the OCR opened as ( or {; otherwise it is a misread letter and is left for the word fixes."""
    out='';depth=0
    for ch in t:
        if ch=='(':depth+=1
        elif ch==')':depth=max(0,depth-1)
        elif ch=='}' and depth:ch=')';depth-=1
        out+=ch
    return out
def normalize(t):
    for a,b in FIXED:t=re.sub(a,b,t)
    t=braces(t)
    m=NUM_LABEL.match(t)
    if m:
        lab=re.sub(r'\s+',' ',m.group(1));n=re.sub(r'[0-9ilIoOz|x]+',lambda k:fix_num(k.group(0)),m.group(2))
        if not n.isdigit() and lab=='Objection' and not re.search(r'\d',n):n='1'  # the first objection of an article
        if re.fullmatch(r'\d+((, | and )\d+)*',n):t=lab+' '+n+': '+t[m.end():]
    return t.strip()
def structure(V,notes,merged):
    """Headings in the Gutenberg layout. Returns the list of output blocks and a flag list."""
    out=[];flags=[];q=None;art=None;expect=None;i=0;n=len(merged);seq={'o':0,'r':0}
    def T(k):return normalize(merged[k]['t'])
    vol_of=lambda k:merged[k]['vol']
    while i<n:
        t=T(i);raw=merged[i]['t']
        m=re.match(r'^QUESTION\s+([IVXLCil1]+)\s*[.,:;ik]?\s*(.*)$',raw.strip(),re.S)
        if m:
            want=(q['n']+1) if q else 1;rd=m.group(1)
            reads={roman(x) for x in {rd,rd.replace('l','I').replace('i','I').replace('1','I'),rd.replace('L','I'),rd[:-1]+'I' if rd.endswith('L') else rd,rd.replace('l','I').replace('L','I')}}
            if want not in reads:
                if q and q['n']==99:break  # the appendices follow Question 99
                notes['fixes']['QUESTION heading %r not read as %d'%(rd,want)]+=1
            elif roman(rd)!=want:notes['fixes']['QUESTION %s -> %d'%(rd,want)]+=1
            qn=want
            if m.group(2):merged[i]=dict(merged[i],t='QUESTION '+rd);merged.insert(i+1,dict(merged[i],t=m.group(2),foot=[]));n+=1
            # title: following caps paragraphs up to "(In N Articles.)"
            j=i+1;title=[];count=None
            while j<n and len(title)<4:
                tt=T(j);cm=re.search(r'[(\[{](?:In\s+)?([A-Za-z]+)\s+Ar[a-z]{3,5}s?\.?[)\]}]\.?',tt,re.I)
                if cm:
                    before=tt[:cm.start()].strip()
                    if before:title.append(before)
                    w=cm.group(1).capitalize();count=NUMW.index(w)+1 if w in NUMW else None
                    rest=tt[cm.end():].strip()
                    if rest:merged[j]=dict(merged[j],t=rest)  # the OCR ran the question's opening into its heading
                    else:j+=1
                    break
                if re.match(r'^(First|Second)\s+Article',tt,re.I):break
                title.append(tt);j+=1
            ttl=re.sub(r'\s+',' ',' '.join(title)).strip().rstrip('.')
            if ttl.endswith('.*'):ttl=ttl[:-2]+'*'
            ttl=re.sub(r'\.\s+(?=[a-z])',', ',ttl.replace('.  ',', '))
            ttl=re.sub(r'\.\s+(AS|IN|OF|AND)\b',r', \1',ttl)
            if q is not None and art is None and count!=1:pass
            q={'n':qn,'count':count};art=None;qstart=len(out)+2
            out.append('QUESTION %d'%qn);out.append(ttl.upper()+'\n(In %s Article%s)'%(NUMW[count-1] if count else 'One','' if count==1 else 's') if count else ttl.upper())
            if count is None:flags.append(('Q%d'%qn,'no article count read'))
            i=j;continue
        am=re.match(r'^(?:([A-Za-z01]+)\s+)?ART[I1l]CLE\b[\s.,:;"\'■*†]*(.*)$',raw.strip(),re.I|re.S)
        if not am and q is not None and re.match(r'^whether\b',raw.strip(),re.I):
            # the heading line was lost in the OCR; the "We proceed thus to the Nth Article" line below names the article
            for j in range(i+1,min(i+4,n)):
                wm=re.match(WEP.pattern+r'\s+to\s+the\s+(\w+)\s+Article',merged[j]['t'],re.I)
                if wm and ordinal(wm.group(1))==ORD[art or 0]:
                    am=re.match(r'^()()(.*)$','ARTICLE');raw=ORD[art or 0]+' Article. '+raw.strip();am=re.match(r'^(?:([A-Za-z01]+)\s+)?ART[I1l]CLE\b[\s.,:;"\'■*†]*(.*)$',raw,re.I|re.S)
                    notes['fixes']['article heading restored from "We proceed" line, Q%d Art. %d'%(q['n'],(art or 0)+1)]+=1;break
                if wm:break
        def named_below():
            for j in range(i+1,min(i+4,n)):
                wm=re.match(WEP.pattern+r'\s+to\s+the\s+(\w+)\s+Article',merged[j]['t'],re.I)
                if wm:return ordinal(wm.group(1))
        if am and q is not None and am.group(1) and not ordinal(am.group(1)) and named_below()==ORD[art or 0]:
            notes['fixes']['article heading %r read from "We proceed" line, Q%d Art. %d'%(am.group(1),q['n'],(art or 0)+1)]+=1
            raw=ORD[art or 0]+' Article. '+am.group(2);am=re.match(r'^(?:([A-Za-z01]+)\s+)?ART[I1l]CLE\b[\s.,:;"\'■*†]*(.*)$',raw,re.I|re.S)
        if am and q is not None and (am.group(1) and ordinal(am.group(1)) or not am.group(1) and q['count']==1 and art is None) and (not am.group(2) or re.match(r'^whether\b',am.group(2),re.I)):
            word=ordinal(am.group(1)) if am.group(1) else 'First';k=(art or 0)+1
            if ORD.index(word)+1!=k:notes['fixes']['%s Article read as article %d in Q%d'%(word,k,q['n'])]+=1
            art=k;title=[am.group(2)] if am.group(2) else [];j=i+1
            while j<n and not WEP.match(T(j)) and not re.match(r'^(Objection|Obj\.)',T(j)) and len(title)<3 and (not title or not re.search(r'\?\s*$',title[-1])):
                title.append(T(j));j+=1
            ttl=re.sub(r'\s+',' ',' '.join(normalize(x) for x in title)).strip()
            ttl=recase(ttl,V)
            ttl=re.sub(r'(\w)- (\w)',r'\1\2',re.sub(r'\s/\.\s',' ',ttl))
            ttl=re.sub(r'(?:\s*\}|\s+2|\.)\s*\??(\*?)$',r'?\1',ttl) if ttl.startswith('Whether') else ttl
            if re.search(r"[^A-Za-z ,?'\-;:()]",ttl.replace('etc.','etc')) or not ttl.endswith('?'):
                # an unreadable or unfinished title: the question's own list of inquiries, in the same printing, has it
                inq=' '.join(out[qstart:])
                im=re.search(r'\(%d\)\s*(Whether[^?]*\?)'%k,inq)
                if im:
                    import difflib
                    cand=re.sub(r'\s+',' ',im.group(1));cand=cand[0].upper()+cand[1:]
                    if difflib.SequenceMatcher(None,cand.lower(),ttl.lower()).ratio()>0.7:
                        notes['fixes']['article title from the inquiry list, Q%d Art. %d'%(q['n'],k)]+=1;ttl=cand
            if j<n and WEP.match(T(j)):j+=1
            elif j<n and WEP.match(T(j+1) if j+1<n else ''):pass
            seq['o']=seq['r']=0
            out.append('_______________________');out.append('%s ARTICLE [Suppl., Q. %d, Art. %d]'%(ORD[k-1].upper(),q['n'],k));out.append(ttl)
            if not re.match(r'^Whether\b',ttl):flags.append(dict(block=len(out)-1,words=['article title'],vol=merged[i]['vol'],pages=merged[i]['pages'],q=q['n'],a=art))
            i=j;continue
        if WEP.match(t):i+=1;continue
        if q is None:i+=1;continue  # before Question 1
        if re.match(r'^(APPENDIX|TWO ARTICLES ON PURGATORY)',raw.strip()):break
        p=clean_words(t,V,notes,i)
        if not re.search(r'[A-Za-z]{3,}',p) or len(p)<12 and not any(V.known(x) for x in re.findall(r'[A-Za-z]{3,}',p)):
            notes['fixes']['dropped scan noise %r'%p]+=1;i+=1;continue
        bad=suspicious(p,V)
        lm=LABEL2.match(p)
        if lm and not re.match(r'^(Objection|Obj\.|Reply Obj\.) \d+((, | and )\d+)*: ',p):
            reply=bool(lm.group(1));num=lm.group(3)
            if re.fullmatch(r'\d+',num or ''):n_=int(num)
            else:n_=(seq['r'] if reply else seq['o'])+1;notes['fixes']['label number %r read as %d from the sequence'%(num,n_)]+=1
            p=('Reply Obj. %d: ' if reply else ('Objection %d: ' if n_==1 else 'Obj. %d: '))%n_+p[lm.end():]
        sm_=re.match(r'^(Reply Obj\.|Obj\.|Objection) (\d+)',p)
        if sm_:seq['r' if sm_.group(1).startswith('Reply') else 'o']=int(sm_.group(2))
        p=re.sub(r'^Objection (\d+):',r'Objection \1:',p);p=re.sub(r'^On the contrary,',r'_On the contrary,_',p);p=re.sub(r'^I answer that,',r'_I answer that,_',p)
        out.append(p)
        src=merged[i]
        if bad and art:
            ok=na_words(q['n'],art,CACHE);bad=[w for w in bad if not (re.fullmatch(r"[A-Za-z'\-]+",w) and all(x.lower() in ok for x in re.findall(r'[A-Za-z]+',w)))]
        if bad:flags.append(dict(block=len(out)-1,words=bad[:6],vol=src['vol'],pages=src['pages'],q=q['n'],a=art))
        for f in src['foot']:
            fx=clean_words(normalize(re.sub(r'^[\*†‡§¶tf\+]\s*','',f)),V,notes,i)
            out.append('[*'+fx+']');b2=suspicious(fx,V)
            if b2 and art:
                ok=na_words(q['n'],art,CACHE);b2=[w for w in b2 if not (re.fullmatch(r"[A-Za-z'\-]+",w) and all(x.lower() in ok for x in re.findall(r'[A-Za-z]+',w)))]
            if b2:flags.append(dict(block=len(out)-1,words=b2[:6],vol=src['vol'],pages=src['pages'],q=q['n'],a=art))
        i+=1
    return out,flags
HEADER=[
 'Summa Theologica, Supplement to the Third Part (Supplementum Tertiae Partis)',
 'St. Thomas Aquinas. Literally translated by Fathers of the English Dominican Province.',
 'Aquinas died in 1274 before finishing the Third Part. The Supplement completing it was compiled after his death from his earlier Commentary on the Sentences, traditionally attributed to his companion Reginald of Piperno.',
 'Transcribed for Bibliotheca Catholica from Internet Archive scans of the English Dominican printings: Third Part, Fourth Number (R. & T. Washbourne and Benziger Brothers, 1917) for Questions 1 to 33; Third Part (Supplement), QQ. XXXIV to LXVIII (Burns Oates & Washbourne and Benziger Brothers, 1922) for Questions 34 to 68; QQ. LXIX to LXXXVI (Burns Oates & Washbourne, 1921) for Questions 69 to 86; and QQ. LXXXVII to XCIX (Benziger Brothers, 1922) for Questions 87 to 99. Public domain in the USA: printed before 1931.',
 'The OCR was cleaned by tools/transcribe_supplement.py: running heads and page numbers removed, footnotes set in brackets after their paragraph as [*...], words rejoined across line breaks, and common OCR misreadings corrected. No text was supplied from other sources. Passages that could not be confidently corrected are listed, with their scan pages, in data/summa-supplement-ocr.json and marked on the Summa pages. The appendices printed after Question 99 are not included.',
]
TITLE_BLOCK='SUPPLEMENT\n["Suppl.," "Supplementum Tertiae Partis"]'
END_LINE='*** END OF THE TRANSCRIPTION ***'
def main():
    global CACHE
    ap=argparse.ArgumentParser();ap.add_argument('--cache',required=True);ap.add_argument('--dry',action='store_true');a=ap.parse_args();CACHE=a.cache
    V,notes,merged=build(a.cache);V.seen=collections.Counter(w for p in merged for w in re.findall(r"[a-z]+",p['t']));out,flags=structure(V,notes,merged)
    head=HEADER+[TITLE_BLOCK];text='\n\n'.join(head+out+[END_LINE])+'\n'
    blocks=[x.strip() for x in re.split(r'\n\s*\n',text) if x.strip()]
    assert len(blocks)==len(head)+len(out)+1,'a block contains a blank line'
    nq=sum(1 for b in out if re.match(r'^QUESTION \d+$',b));na=sum(1 for b in out if re.match(r'^[A-Z]+ ARTICLE \[Suppl',b))
    fl=[]
    for f in flags:
        if not isinstance(f,dict):continue
        k=len(head)+f['block'];fl.append(dict(block=k,starts=blocks[k][:40],q=f['q'],a=f['a'],words=f['words'],scan=dict(identifier=f['vol'],pages=sorted(set(f['pages'])),
            url='https://archive.org/details/%s/page/n%d/mode/1up'%(f['vol'],sorted(set(f['pages']))[0]))))
    print('%d questions; %d articles; %d flagged blocks; %d corrections'%(nq,na,len(fl),sum(notes['fixes'].values())))
    if a.dry:return
    tp=ROOT/'data/texts'/(EDITION+'.txt');tp.write_text(text,encoding='utf-8')
    sha=hashlib.sha256(tp.read_bytes()).hexdigest()
    src=dict(id=EDITION,kind='ocr-transcription',title='Summa Theologica, Supplement to the Third Part',translator='Fathers of the English Dominican Province',
             rights='Public domain in the USA. Every printing used was published before 1931 (1917, 1921, and 1922).',
             volumes=notes['volumes'],substitutePages=notes['substitutes'],
             method='tools/transcribe_supplement.py: Internet Archive djvu.xml OCR, running heads and page numbers removed, footnotes bracketed after their paragraph, OCR misreadings corrected only where the result is a word the Gutenberg Summa or an English word list has and the OCR form is not; flagged passages are marked, not rewritten. Article counts and titles were checked against the standard structure (99 questions, 446 articles); New Advent was used only to confirm a flagged word that both have, never as a source of text.',
             appendices='The two appendices printed after Question 99 (on the souls of unbaptized children and on purgatory) are not included.',
             questions=nq,articles=na,flaggedBlocks=len(fl),corrections=sum(notes['fixes'].values()),text='data/texts/'+EDITION+'.txt',sha256=sha,checked='2026-11-09')
    (ROOT/'data/sources'/(EDITION+'.json')).write_text(json.dumps(src,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'data/summa-supplement-ocr.json').write_text(json.dumps(dict(note='Generated by tools/transcribe_supplement.py. Blocks are splitText() blocks of data/texts/'+EDITION+'.txt; "starts" guards against drift.',
        edition=EDITION,sha256=sha,flags=fl,corrections=dict(sorted(notes['fixes'].items(),key=lambda x:-x[1]))),ensure_ascii=False,indent=1)+'\n')
    lp=ROOT/'data/library.json';lib=json.loads(lp.read_text())
    for w in lib['works']:
        for e in w['editions']:
            if e['id']==EDITION and e['sha256']!=sha:e['sha256']=sha;lp.write_text(json.dumps(lib,ensure_ascii=False,indent=2)+'\n');print('updated data/library.json')
    print('wrote',tp,sha)
if __name__=='__main__':main()
