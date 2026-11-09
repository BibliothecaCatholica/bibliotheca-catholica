#!/usr/bin/env python3
"""Index the hosted Summa Theologiae (Project Gutenberg #17611, #17897, #18755, #19950) into data/summa.json.

The four Gutenberg files are the Dominican Fathers' translation (Perry/CCEL text corrected by McClamrock). This tool
splits each file the way the reading room does (blank-line blocks, splitText() in scripts/library.js) and records,
per part, its treatises, questions, and articles with their block ranges, so tools/build_static.py can write one
static page per question and per article at /summa/<part>/q<n>/ and /summa/<part>/q<n>/a<m>/ and link each one
into the reading room. It checks the SHA-256 of each file against data/library.json, that questions run 1..N with
no gaps, that each question has the number of articles its heading states ("In Four Articles"), and that every
article's bracketed reference ([I, Q. 2, Art. 3]) matches where it sits. Part of `npm run build`.

    python3 tools/build_summa.py
"""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK='summa-theologiae';SIZE=35
# slug, bracket token, English name, Latin name, edition, New Advent prefix, questions; ARTICLES are the standard totals
ARTICLES={'1':584,'1-2':619,'2-2':917,'3':549}
PARTS=[('1','I','First Part','Prima Pars','pg-17611',1,119),
       ('1-2','I-II','First Part of the Second Part','Prima Secundae','pg-17897',2,114),
       ('2-2','II-II','Second Part of the Second Part','Secunda Secundae','pg-18755',3,189),
       ('3','III','Third Part','Tertia Pars','pg-19950',4,90)]
NUM={w:i for i,w in enumerate('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen'.split())}
SEP=re.compile(r'(\n_{5,})+$')
Q_HEAD=re.compile(r'^QUESTION (\d+)$')
A_HEAD=re.compile(r'^(?:([A-Z]+(?:-[A-Z]+)?) )?ARTICLE(?: *\[(.*)\])?$')
ORD={w:i+1 for i,w in enumerate('FIRST SECOND THIRD FOURTH FIFTH SIXTH SEVENTH EIGHTH NINTH TENTH ELEVENTH TWELFTH THIRTEENTH FOURTEENTH FIFTEENTH SIXTEENTH SEVENTEENTH'.split())}
REF=re.compile(r'^\s*(?:([I-]+)[.,]?\s*)?Q[.,]*\s*,?\s*(\d+)[.,]?\s*(?:Art|A)\.?\s*(\d*)\s*$',re.I)
COUNT=re.compile(r'\s*\((?:in )?([a-z]+) articles?\)',re.I)
TREATISE=re.compile(r'^TREATISE ON .+$')
SMALL={'a','an','and','as','at','by','for','from','in','into','of','on','or','the','to','with','whether','is','be'}
def split_text(raw):return [p.strip() for p in re.split(r'\n\s*\n',raw.replace('\r','')) if p.strip()]
def clean(b):return SEP.sub('',b).strip()
def one(s):return re.sub(r'\s+',' ',s).strip()
def title_case(s):
    """THE EXISTENCE OF GOD -> The Existence of God (question and treatise headings are set in capitals)."""
    out=[]
    for k,w in enumerate(one(s).split(' ')):
        lw=w.lower()
        if k and lw in SMALL - {'whether','is','be'}:out.append(lw);continue
        out.append(re.sub(r"^([(\"'\[]*)(\w)",lambda m:m.group(1)+m.group(2).upper(),lw))
    t=' '.join(out)
    return re.sub(r"\b(Ii|Iii|Iv|Vi|Vii|Viii|Ix|Xi)\b",lambda m:m.group(1).upper(),t)
def stated(cm,B,i,end):
    """Articles a question announces: "(In Four Articles)", else "there are four points of inquiry"."""
    if cm:return NUM.get(cm.group(1).lower())
    for k in range(i,min(i+3,end)):
        m=re.search(r'\b([a-z]+) points? of inquiry',B[k],re.I)
        if m:return NUM.get(m.group(1).lower())
    return None
def inquiry(B,a,b):
    """The numbered points of inquiry in a question's opening: {1: 'Whether ...?'}."""
    out={}
    for k in range(a,b+1):
        m=re.match(r'^\((\d+)\) (.+)$',clean(B[k]),re.S)
        if m:t=one(m.group(2));out[int(m.group(1))]=t[0].upper()+t[1:]
    return out
def display_title(t):
    """An article or question title without the translators' footnotes ([*...]), their asterisks, or _italic_ marks."""
    t=re.sub(r'\s*\[\*[^\]]*\]','',t);t=t.replace('*','').replace('_','')
    return one(t)
def role(p):
    """Anchor for a paragraph of an article: obj1.., sc, resp, ad1.."""
    m=re.match(r'^(?:Objection|Obj\.) (\d+):',p)
    if m:return 'obj'+m.group(1)
    if re.match(r'^_?On the contrary',p):return 'sc'
    if re.match(r'^_?I answer that',p):return 'resp'
    m=re.match(r'^Reply Obj\. (\d+):',p)
    if m:return 'ad'+m.group(1)
    return ''
def parse(slug,token,ed,expect_q):
    raw=(ROOT/ed['text']).read_bytes();assert hashlib.sha256(raw).hexdigest()==ed['sha256'],(ed['id'],'text changed')
    B=split_text(raw.decode('utf-8'))
    end=next(i for i,b in enumerate(B) if re.search(r'\*\*\* ?END OF (THE |THIS )?PROJECT GUTENBERG',b,re.I))
    # the part's own title block, after the transcriber's contents list: FIRST PART\n["I," "Prima Pars"]
    start=next(i for i,b in enumerate(B) if ('\n["'+token+',"') in b)
    toc={}
    for b in B[:start]:
        for line in b.split('\n'):
            m=re.match(r'^(\d+)\.\s+(.+)$',line.strip())
            if m:toc[int(m.group(1))]=one(m.group(2))
    treatises,questions=[],[];cur_t=None;q=None;art=None;i=start+1;problems=[];prologue=None
    def close(upto):
        nonlocal art
        if art is not None:
            art['end']=upto;assert art['end']>=art['start'],(slug,q['n'],art['n'],'empty article');art=None
    while i<end:
        b=clean(B[i])
        if not b:i+=1;continue
        if TREATISE.match(b) and '\n' not in b:
            close(i-1)
            if q is not None and 'end' not in q:q['end']=i-1
            cur_t={'title':title_case(re.sub(r'\s*\(QQ?\. [\d-]+\)$','',b)),'heading':i,'questions':[]};treatises.append(cur_t);i+=1;continue
        m=Q_HEAD.match(b)
        if m and q is not None and int(m.group(1))==q['n']:
            # the transcription repeats "QUESTION N" where an article heading belongs: take it as the next article
            close(i-1);n=len(q['articles'])+1
            problems.append('%s Q%d: article %d is headed "QUESTION %d" in the text'%(slug,q['n'],n,q['n']))
            art={'n':n,'title':one(clean(B[i+1])),'heading':i,'section':i//SIZE,'start':i+2};q['articles'].append(art);i+=2;continue
        if m and i+1<end:
            close(i-1)
            if q is not None and 'end' not in q:q['end']=i-1
            t=clean(B[i+1]);cm=COUNT.search(t)
            head=t[:cm.start()] if cm else t.split('\n')[0]
            q={'n':int(m.group(1)),'title':title_case(re.sub(r'\s*\(Question \d+\)$','',head)),'note':one(t[cm.end():]) if cm else '','stated':stated(cm,B,i+2,end),'heading':i,'section':i//SIZE,'prologue':[i+2,i+1],'articles':[]}
            questions.append(q)
            if cur_t is not None:cur_t['questions'].append(q['n'])
            i+=2;continue
        if b=='PROLOGUE' and q is None:
            prologue=[i+1,i];i+=1
            while i<end and not COUNT.search(clean(B[i])) and not Q_HEAD.match(clean(B[i])):prologue[1]=i;i+=1
            continue
        cm=COUNT.search(b)
        if cm and b[:cm.start()].isupper() and len(b)<200 and not Q_HEAD.match(clean(B[i-1])):
            # a question whose "QUESTION N" line is missing from the transcription: number it from its neighbour
            close(i-1)
            if q is not None and 'end' not in q:q['end']=i-1
            n=q['n']+1 if q else 1;problems.append('%s Q%d: no "QUESTION %d" line in the text; numbered from the previous question'%(slug,n,n))
            q={'n':n,'title':title_case(b[:cm.start()]),'stated':stated(cm,B,i+1,end),'heading':i,'section':i//SIZE,'prologue':[i+1,i],'articles':[]}
            questions.append(q)
            if cur_t is not None:cur_t['questions'].append(n)
            i+=1;continue
        m=A_HEAD.match(b)
        if m:
            close(i-1)
            assert q is not None,(slug,b)
            n=len(q['articles'])+1;word=ORD.get(m.group(1) or '');r=REF.match(m.group(2) or '')
            if m.group(2) is None:problems.append('%s Q%d a%d: heading "%s" has no reference'%(slug,q['n'],n,b))
            elif not r:problems.append('%s Q%d a%d: unreadable reference "%s"'%(slug,q['n'],n,b))
            else:
                if (r.group(1) or token)!=token or int(r.group(2))!=q['n'] or (r.group(3) and int(r.group(3))!=n) or b!='%s ARTICLE [%s, Q. %d, Art. %d]'%(m.group(1),token,q['n'],n):
                    problems.append('%s Q%d a%d: heading reads "%s"'%(slug,q['n'],n,b))
            if word and word!=n:problems.append('%s Q%d a%d: heading word %s'%(slug,q['n'],n,m.group(1)))
            t=one(clean(B[i+1]))
            if re.match(r'^(?:Objection|Obj\.) 1:',t):
                # no title line: take the article's question from the question's list of inquiries
                inq=inquiry(B,q['prologue'][0],i-1).get(n)
                assert inq,(slug,q['n'],n,'no title and no inquiry line')
                problems.append('%s Q%d a%d: no title line in the text; title from the list of inquiries'%(slug,q['n'],n))
                art={'n':n,'title':inq,'heading':i,'section':i//SIZE,'start':i+1};q['articles'].append(art);i+=1;continue
            art={'n':n,'title':t,'heading':i,'section':i//SIZE,'start':i+2};q['articles'].append(art);i+=2;continue
        if art is None and q is not None:q['prologue'][1]=i
        i+=1
    close(end-1)
    if q is not None and 'end' not in q:q['end']=end-1
    for x in questions:
        if not x['articles'] and x['stated']==1:
            # a one-article question printed without an article heading: the question title is the article's
            k=next(k for k in range(x['prologue'][0],x['end']+1) if re.match(r'^Objection 1:',B[k]))
            x['prologue'][1]=k-1;x['articles'].append({'n':1,'title':x['title'],'heading':x['heading'],'section':x['section'],'start':k,'end':x['end'],'untitled':True})
            problems.append('%s Q%d: its one article has no heading in the text'%(slug,x['n']))
            body=[clean(B[j]) for j in range(k,x['end']+1)];a=x['articles'][0];a['words']=sum(len(p.split()) for p in body)
            a['has']=''.join(c for c,r in (('o','obj1'),('s','sc'),('r','resp'),('a','ad1')) if r in [role(p) for p in body])
    for x in questions:
        for y in x['articles']:y['title']=display_title(y['title'])
    nums=[x['n'] for x in questions]
    for x in questions:
        x['heading_title']=x['title']
        if x['n'] in toc:x['title']=toc[x['n']]
        elif toc:problems.append('%s Q%d: not in the contents list'%(slug,x['n']))
        x['title']=display_title(x['title'])
        for y in x['articles']:
            if y.get('untitled'):y['title']=x['title']
    if toc and len(toc)!=len(questions):problems.append('%s: contents list has %d questions, text %d'%(slug,len(toc),len(questions)))
    assert nums==list(range(1,len(nums)+1)),(slug,'questions out of sequence',[(a,b) for a,b in zip(nums,range(1,len(nums)+1)) if a!=b][:3])
    for x in questions:
        an=[a['n'] for a in x['articles']]
        if x['stated'] is None:problems.append('%s Q%d: heading states no article count'%(slug,x['n']))
        elif len(an)!=x['stated']:problems.append('%s Q%d: heading says %d articles, text has %d'%(slug,x['n'],x['stated'],len(an)))
        for a in x['articles']:
            body=[clean(B[k]) for k in range(a['start'],a['end']+1)]
            a['words']=sum(len(p.split()) for p in body)
            roles=[role(p) for p in body]
            a['has']=''.join(c for c,k in (('o','obj1'),('s','sc'),('r','resp'),('a','ad1')) if k in roles)
    assert len(questions)==expect_q,(slug,len(questions),'questions, expected',expect_q)
    assert sum(len(x['articles']) for x in questions)==ARTICLES[slug],(slug,'article total')
    return dict(blocks=len(B),start=start,end=end,prologue=prologue,treatises=treatises,questions=questions),problems
def build():
    lib=json.loads((ROOT/'data/library.json').read_text());w=next(x for x in lib['works'] if x['id']==WORK);eds={e['id']:e for e in w['editions']}
    parts,problems=[],[]
    for slug,token,en,la,edid,na,eq in PARTS:
        ed=eds[edid];assert 'gutenberg.org' in ed['source'] and ed.get('text'),edid
        d,p=parse(slug,token,ed,eq);problems+=p
        parts.append(dict(slug=slug,token=token,name=en,latin=la,edition=edid,newAdvent=na,**d))
    return parts,problems
def main():
    parts,problems=build()
    known=json.loads((ROOT/'tools/summa_known.json').read_text())['problems']
    new=[p for p in problems if p not in known]
    for p in problems:
        if p not in known:print('PROBLEM: '+p)
    gone=[p for p in known if p not in problems]
    if gone:sys.exit('build_summa: known problems no longer seen (update tools/summa_known.json): '+'; '.join(gone))
    if new:sys.exit('build_summa: unexpected problems; check the text or add them to tools/summa_known.json with a reason')
    (ROOT/'data/summa.json').write_text(json.dumps({'note':'Generated by tools/build_summa.py; block indexes are splitText() blocks of the hosted Gutenberg files.','work':WORK,'parts':parts},ensure_ascii=False,separators=(',',':'))+'\n')
    print('summa: '+', '.join('%s %d questions, %d articles'%(p['token'],len(p['questions']),sum(len(q['articles']) for q in p['questions'])) for p in parts))
if __name__=='__main__':main()
