#!/usr/bin/env python3
"""Rites & Liturgy section (v19, phase 2): data, map, and pages.

Reads only committed, offline inputs:
  data/rites-src/rites-map.json          research records (24 Churches sui iuris and 7 Latin rites and uses)
  data/rites-src/rites-map-shading.json  country lists per Church (GCatholic) and approximate heartlands
  data/rites-src/geo.json                compact Natural Earth geometry (tools/rites_geo.py)
and the editorial review (research/rites-map-editorial-review.md in the working notes; summarised in
docs/RITES.md). Every review decision is one of the tables below, so the published data and the review
cannot drift apart: OVERRIDES (reworded values), DROP (fields left out), UNVERIFIED (low-confidence
fields shown with a visible "Unverified" marker), and RESOURCE_FIX (corrected resources).

Writes data/rites.json (the public, display-ready records), data/rites.js (window.RITES_DATA: the same
plus the map and the page HTML, lazy-loaded by scripts/rites.js; books.js is untouched), and the
generated palette block in styles/rites.css. tools/build_static.py renders /rites/ pages from data/rites.js.
No population numbers, no pins, no dioceses, no dominant-rite layer.
"""
import colorsys,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import rites_pages
SRC=ROOT/'data/rites-src'
CHECKED='2026-10-26'
MONTHS=['January','February','March','April','May','June','July','August','September','October','November','December']

# ---------- families ----------
# CCEO can. 28 par. 2 names five Eastern traditions; the Latin Church is governed by the 1983 Code.
FAMILIES={
 'lat':{'label':'Latin','long':'Latin tradition','src':'okabe:#0072B2'},
 'alex':{'label':'Alexandrian','long':'Alexandrian tradition','src':'okabe:#CC79A7'},
 'ant':{'label':'Antiochene','long':'Antiochene (West Syriac) tradition','src':'okabe:#009E73'},
 'arm':{'label':'Armenian','long':'Armenian tradition','src':'okabe:#56B4E9'},
 'chal':{'label':'Chaldean','long':'Chaldean (East Syriac) tradition','src':'okabe:#D55E00'},
 'byz':{'label':'Constantinopolitan (Byzantine)','long':'Constantinopolitan (Byzantine) tradition','src':'okabe:#E69F00'},
}
FAM_ORDER=['lat','alex','ant','arm','chal','byz']
CCC_SRC='https://www.vatican.va/archive/ENG0015/__P3C.HTM'
CCEO_SRC='https://www.vatican.va/content/john-paul-ii/la/apost_constitutions/documents/hf_jp-ii_apc_19901018_codex-can-eccl-orient-1.html'
# The rite each record falls under in the Catechism's list (CCC 1203), shown beside the CCEO tradition.
CCC_NAME={'lat':'Latin','alex':'Alexandrian or Coptic','ant':'Syriac','arm':'Armenian','chal':'Chaldean','byz':'Byzantine'}
CCC_BY_ID={'maronite':'Maronite'}

# ---------- editorial review decisions ----------
OVERRIDES={  # (record, field) -> replacement text, with the reason in docs/RITES.md
 ('albanian','canonical_status'):'Listed among the 23 Eastern Catholic Churches in lists derived from the Annuario Pontificio. GCatholic omits it and lists a Byzantine Church in Kazakhstan and Central Asia instead.',
 ('latin-roman-1962','name'):'Roman Missal of 1962',
 ('latin-roman','name'):'Roman Rite (the Missal of Paul VI and John Paul II)',
 ('latin-religious-orders','name'):'Rites of certain religious orders',
 ('latin-divine-worship','name'):'Divine Worship (Personal Ordinariates)',
 ('latin-braga','liturgical_books_current'):'Missal of Braga (Bracarense), 1924 edition; its use is optional',
 ('latin-hispanic-mozarabic','liturgical_books_current'):'Missale Hispano-Mozarabicum (2 vols, 1991 and 1994); Liber Commicus (1994 and 1995); Liber Offerentium (1991)',
}
MILESTONE_FIX={  # (record, when as sourced) -> event text
 ('albanian','1996'):'Bishop appointed; the faithful are almost entirely of the Latin rite',
 ('latin-hispanic-mozarabic','1991–1995'):'Post-conciliar books: Missale Hispano-Mozarabicum I (1991) and II (1994); Liber Commicus I (1994) and II (1995)',
 ('latin','1962'):'Last typical edition of the Missale Romanum before the reform (John XXIII)',
 ('latin','2007'):'Summorum Pontificum called the 1962 Missal the "extraordinary expression" of the lex orandi (norms abrogated in 2021)',
}
STATUS_MAG_FIX={  # latin-roman-1962 status_magisterial index -> (text, sources): follows Traditionis custodes art. 8
 4:('Traditionis custodes, art. 8: "Previous norms, instructions, permissions, and customs that do not conform" to it "are abrogated". These include the norms of Summorum Pontificum (2007), which had called the 1962 Missal the "extraordinary expression" of the lex orandi.',
    ['https://www.vatican.va/content/francesco/en/motu_proprio/documents/20210716-motu-proprio-traditionis-custodes.html','https://www.vatican.va/content/benedict-xvi/en/motu_proprio/documents/hf_ben-xvi_motu-proprio_20070707_summorum-pontificum.html']),
}
DROP={  # fields left out entirely (shown as "Not yet verified" where the slot exists)
 ('albanian','present_see'):'CNEWA places only a parish at Elbasan; the see of the Apostolic Administration is probably elsewhere',
 ('belarusian','present_see'):'no eparchy; an Apostolic Visitator is not a see',
 ('russian','mother_city'):'low confidence; the 1917 exarchate seat needs a source',
 ('russian','present_see'):'low confidence; no functioning hierarchy',
 ('latin-roman-1962','status_reported_not_magisterial'):'press reports, not legislative acts; source is a home page, not an article',
}
UNVERIFIED={  # low-confidence fields shown with an "Unverified" marker and their source (all others are left out)
 ('albanian','head'),
 ('coptic','liturgical_books_current'),('ethiopian','liturgical_books_current'),('eritrean','liturgical_books_current'),
 ('syriac','liturgical_books_current'),('syro-malankara','liturgical_books_current'),('armenian','liturgical_books_current'),
 ('chaldean','liturgical_books_current'),('syro-malabar','liturgical_books_current'),
}
RESOURCE_FIX={  # (record, url) -> replacement fields
 ('armenian','https://archive.org/details/armenianchurchfo00fort'):{'title':'E. F. K. Fortescue, The Armenian Church, founded by St. Gregory the Illuminator (London: J. T. Hayes, 1872)','evidence':'Published 1872. Author as recorded by archive.org: Edward Francis Knottesford Fortescue (not Adrian Fortescue).'},
 ('latin-roman','https://archive.org/details/romanmissaladapt00unknuoft'):{'title':'The Roman Missal adapted to the use of the laity (Toronto: W. E. Blake; undated, after 1913)','rights':'unknown','evidence':'Undated: archive.org gives only "19--", and the front matter follows the rubrics of the decree of 28 October 1913. Unknown until a dated copy is found.'},
 ('latin-roman','https://archive.org/details/missaleromanum0000unse'):{'title':'Missale Romanum (Tours: Mame, 1922), a historical printing','evidence':'Title page: MCMXXII (1922), before the 1931 cutoff.'},
 ('latin-roman-1962','https://archive.org/details/missaleromanum0000unse'):{'title':'Missale Romanum (Tours: Mame, 1922), a printing before 1962; its text differs in details','evidence':'Title page: MCMXXII (1922), before the 1931 cutoff.'},
 ('latin-roman-1962','https://www.divinumofficium.com/'):{'title':'Divinum Officium (an independent project; software MIT, text provenance mixed)','evidence':'The software licence is not a licence for the texts.'},
}
PUBLIC_NOTES={  # neutral public wording of the research notes (the raw notes are working notes, not copy)
 'ethiopian':'The Ge\'ez liturgy is shared with the Eritrean Catholic Church. In southern Ethiopia most Catholic jurisdictions are Latin (CNEWA).',
 'eritrean':'It uses the Ge\'ez liturgy of Alexandrian origin, the same as the Ethiopian Catholic Church; it is not a separate liturgical family.',
 'maronite':'The Catechism (CCC 1203) lists the Maronite rite by name; CCEO can. 28 §2 places it within the Antiochene tradition. Both classifications are shown.',
 'syro-malankara':'West Syriac (Antiochene), not East Syriac. It shares Kerala and the heritage of Saint Thomas the Apostle with the Syro-Malabar Church, but follows a different rite.',
 'syro-malabar':'With the Chaldean Church, one of the two Catholic Churches of the East Syriac tradition. The Syro-Malankara Church, also in Kerala, is West Syriac.',
 'melkite':'Constantinopolitan (Byzantine) in rite, although its patriarch holds the title of Antioch.',
 'ruthenian':'CNEWA describes three jurisdictions: the Metropolia of Pittsburgh, a Church sui iuris; the Eparchy of Mukachevo, immediately subject to the Holy See; and an exarchate in the Czech Republic. CNEWA says their relationship "has not been clarified".',
 'bulgarian':'GCatholic now lists its type as eparchial (the exarchate was raised to an eparchy). The date of the change is not yet verified.',
 'italo-albanian':'It has no Orthodox counterpart (CNEWA). GCatholic names it the Byzantine Church in Italy.',
 'macedonian':'GCatholic lists its type as eparchial (the exarchate was raised to an eparchy). The date of the change is not yet verified.',
 'croatia-serbia':'Listed as one Church, following GCatholic (Byzantine Church in Croatia and Serbia). Other lists divide or group it differently.',
 'albanian':'Lists differ: lists derived from the Annuario Pontificio include it; GCatholic does not. Its present country list is not verified, so only its approximate historical heartland can be shown on the map.',
 'latin-divine-worship':'Approved for the Personal Ordinariates erected under Anglicanorum coetibus (2009), within the Roman Rite. GCatholic labels it "Anglican Use" (three jurisdictions).',
 'latin-religious-orders':'The Catechism (CCC 1203) mentions the rites "of certain religious orders" without naming them. No order is named here until each has its own verified source.',
 'latin-ambrosian':'',
}
NOTE_SRC={'ethiopian':'official','eritrean':'official','ruthenian':'official','italo-albanian':'official','maronite':CCC_SRC,'syro-malankara':'official','syro-malabar':'official','melkite':'official',
          'bulgarian':'name','macedonian':'name','croatia-serbia':'name','albanian':'https://gcatholic.org/dioceses/rites.htm','latin-divine-worship':'official','latin-religious-orders':CCC_SRC}
# Cross-links: only these hand-checked pages (spec section 4 and review section d). Never adrian-fortescue, never orthodoxy.
AUTHORS={'john-chrysostom','basil-the-great','ambrose-of-milan','isidore-of-seville','cyril-of-alexandria','ephrem-the-syrian','gregory-of-narek','theodore-the-studite'}
WORKS={'basil-the-great-de-spiritu-sancto','john-chrysostom-homilies-on-romans','yorke-the-mass'}
SAINTS={'thomas-the-apostle'}
BYZ_LINKS=[('author','john-chrysostom','The Divine Liturgy most often served bears his name'),('author','basil-the-great','The Liturgy of Saint Basil'),('author','theodore-the-studite','Byzantine monastic tradition'),('work','basil-the-great-de-spiritu-sancto','Read: On the Holy Spirit'),('work','john-chrysostom-homilies-on-romans','Read: Homilies on Romans')]
SYR=[('author','ephrem-the-syrian','Syriac Father and hymnographer')]
KERALA=[('saint','thomas-the-apostle','Kerala\'s Saint Thomas Christians trace their origin to him')]
RELATED={'coptic':[('author','cyril-of-alexandria','Father of the Alexandrian tradition'),('author','basil-the-great','The Anaphora of Saint Basil is also used in the Coptic tradition')],
 'syriac':SYR,'maronite':SYR,'syro-malankara':SYR+KERALA,'chaldean':SYR,'syro-malabar':SYR+KERALA,'armenian':[('author','gregory-of-narek','Armenian Doctor of the Church')],
 'latin-ambrosian':[('author','ambrose-of-milan','The rite is named for him')],'latin-hispanic-mozarabic':[('author','isidore-of-seville','Shaped the Hispanic liturgy')],
 'latin-roman':[('work','yorke-the-mass','Read: The Mass')]}

# ---------- text hygiene ----------
def clean(s):
    """Site text rules: no em-dashes (colon or comma instead), no arrows, ranges in words."""
    if s is None:return None
    s=str(s).replace(' — ',': ').replace('—',', ').replace(' → ',', then ').replace('→',', then ')
    s=re.sub(r'(\d|c\.|th|st|nd|rd)\s*–\s*(\d)',r'\1 to \2',s)  # 1895–1899 -> 1895 to 1899; 1st–4th -> 1st to 4th
    s=s.replace('–',' to ').replace(' & ',' and ')
    return re.sub(r'\s+,',',',re.sub(r'\s{2,}',' ',s)).strip()
def when(s):
    s=s.strip();m=re.fullmatch(r'(\d{4})-(\d\d)-(\d\d)',s)
    if m:return '%d %s %s'%(int(m.group(3)),MONTHS[int(m.group(2))-1],m.group(1))
    s=re.sub(r'^(\d{4}) / (\d{4})$',r'\1 and \2',s)
    return clean(s)
def dmy(iso):
    m=re.fullmatch(r'(\d{4})-(\d\d)-(\d\d)',iso or '');return '%d %s %s'%(int(m.group(3)),MONTHS[int(m.group(2))-1],m.group(1)) if m else iso
def head_text(v):
    v=re.sub(r'\s*\(\d{1,3}\)\s*$','',v).replace(' ,',',')
    m=re.match(r'^([A-Z][A-Za-z ]+): (.+)$',v)
    if m:
        role,rest=m.groups()
        return rest if rest.startswith(role) else rest+' ('+role+')'
    return v
RIGHTS={'public domain US':'public_domain_us','open license':'open_license','permission granted':'permission_granted','link only':'link_only','unknown':'unknown'}
LOG={'nyv':[],'unv':[],'dropped':[]}
def fld(rid,key,obj,text=None):
    """One sourced field -> {'v','s','unv'} or None (not shown: 'Not yet verified')."""
    if (rid,key) in DROP:LOG['dropped'].append((rid,key));return None
    if obj is None or obj.get('value',obj.get('name')) is None:LOG['nyv'].append((rid,key));return None
    unv=obj.get('confidence')=='low'
    if unv and (rid,key) not in UNVERIFIED:LOG['nyv'].append((rid,key));return None
    if unv:LOG['unv'].append((rid,key))
    v=OVERRIDES.get((rid,key),text if text is not None else obj.get('value'))
    out={'v':clean(v),'s':[obj['source']] if obj.get('source') else []}
    if unv:out['unv']=True
    return out
def place(rid,key,o):
    if (rid,key) in DROP:LOG['dropped'].append((rid,key));return None
    if not o:return None
    if o.get('confidence')=='low':LOG['nyv'].append((rid,key));return None
    role=ROLE_FIX.get((rid,key),(o.get('role') or '').strip());name=o['name']
    role=re.sub('^'+re.escape(name)+r'\s*[—:-]\s*','',role)
    if role in('—','-',name):role=''
    role=re.sub(r'\s*\('+re.escape(name)+r'\)','',role)
    if role.startswith(name) and len(role)>len(name) and role[len(name)] in ' ;,':name,role=role,''  # the role already names the place: show it whole
    return {'v':clean(name),'role':clean(role),'s':[o['source']]}
ROLE_FIX={('ethiopian','mother_city'):'present metropolitan see; the historical centres of Ethiopian Christianity, such as Aksum, lie elsewhere',
 ('maronite','mother_city'):'historical region of origin: the monastery of Saint Maron, between Aleppo and Antioch',
 ('hungarian','mother_city'):'titular see; residence Debrecen'}

def record(r,layers):
    rid=r['id'];church=r['kind']=='church_sui_iuris';fam=r.get('family') or 'lat'
    x={'id':rid,'kind':'church' if church else 'latin-rite','family':fam,'name':clean(OVERRIDES.get((rid,'name'),r['name']['value'])),'name_src':[r['name']['source']]}
    if church:
        x['cceo']=fld(rid,'rite_tradition',r['rite_tradition']) if fam!='lat' else {'v':'Not covered: CCEO governs the Eastern Churches; the Latin Church is governed by the 1983 Code of Canon Law','s':[CCEO_SRC]}
        x['ccc']={'v':CCC_BY_ID.get(rid,CCC_NAME[fam]),'s':[CCC_SRC]}
        x['status']=fld(rid,'canonical_status',r.get('canonical_status'))
        h=r.get('head')
        if h and h.get('value') and (rid,'head') not in DROP and (h.get('confidence')!='low' or (rid,'head') in UNVERIFIED):
            x['head']=fld(rid,'head',h,head_text(h['value']))
            m=re.search(r'(\d{4}-\d\d-\d\d)',h.get('note') or '')
            if m:x['head']['asof']=dmy(m.group(1))
            if 'gcatholic.org' in h.get('source',''):x['head']['by']='GCatholic'
            elif 'cnewa.org' in h.get('source',''):x['head']['by']='CNEWA (page last modified 26 October 2021)'
        else:x['head']=fld(rid,'head',h)
    o=r.get('origin') or {}
    x['centre']=place(rid,'mother_city',o.get('mother_city'))
    x['see']=place(rid,'present_see',o.get('present_see')) if church else None
    if church and fam!='lat' and x['see'] is None and (rid,'present_see') not in DROP:pass
    if r.get('geography'):x['geography']=fld(rid,'geography',r['geography'])
    lb=r.get('liturgical_books_current')
    x['books']=fld(rid,'liturgical_books_current',lb) if lb else None
    if x['books'] and lb.get('note') and 'CE describes' in lb['note']:x['books']['note']='The Catholic Encyclopedia (1912) describes the rite, not current editions.'
    if x['books'] and fam=='byz':x['books']['note']='Generic book names only: each Church\'s own authority approves its editions and translations, and no edition is named here until verified.'
    ms=[]
    for m in r.get('milestones',[]):
        if m.get('confidence')=='low':LOG['nyv'].append((rid,'milestone '+m['when']));continue
        ms.append({'when':when(m['when']),'event':clean(MILESTONE_FIX.get((rid,m['when']),m['event'])),'s':[m['source']]})
    x['milestones']=ms
    if r.get('status_magisterial'):
        sm=[]
        for i,s in enumerate(r['status_magisterial']):
            t,src=STATUS_MAG_FIX.get(i,(s['value'],[s['source']]))
            sm.append({'v':clean(t),'s':src})
        x['status_magisterial']=sm
    if r.get('status_reported_not_magisterial'):
        assert (rid,'status_reported_not_magisterial') in DROP;LOG['dropped'].append((rid,'status_reported_not_magisterial'))
    res=[]
    for a in r.get('access',[]):
        a=dict(a);fix=RESOURCE_FIX.get((rid,a['url']),{})
        st=RIGHTS[fix.get('rights',a['rights'])]
        res.append({'title':clean(fix.get('title',a['title'])),'url':a['url'],'rights':st,'evidence':clean(fix.get('evidence',a.get('rights_evidence',''))),'checked':CHECKED})
    x['resources']=res
    off=(r.get('official_source') or {}).get('value')
    x['official']=off
    srcs=[]
    for u in [off]+list(r.get('secondary_sources') or []):
        if u and u not in srcs:srcs.append(u)
    x['sources']=srcs
    note=PUBLIC_NOTES.get(rid)
    if note:
        ns=NOTE_SRC.get(rid);ns=off if ns=='official' else r['name']['source'] if ns=='name' else ns
        x['note']={'v':clean(note),'s':[ns] if ns else []}
    x['related']=[{'kind':k,'id':i,'why':clean(w)} for k,i,w in (BYZ_LINKS if fam=='byz' and church else RELATED.get(rid,[]))]
    if r.get('sub_rites'):x['sub']=r['sub_rites']
    if r.get('church'):x['church']=r['church']
    L=layers.get(rid)
    x['layer']=rid if L is not None and (L['present'] or L['heartland']) else None
    return x

def load_layers(shade,names):
    out={}
    for L in shade['layers']:
        lid=L.get('church_id') or L.get('rite_id');p=L['present_jurisdictions_countries'];h=L.get('heartland_historical') or {}
        present=sorted(p['value']) if p.get('confidence')!='low' else []
        hl=sorted(h.get('countries') or []) if h.get('confidence') not in(None,'low') else []
        for c in present+hl:assert c in names,(lid,c,'code not in the map geometry')
        out[lid]={'family':L['family'],'present':present,'psrc':p.get('source'),'asof':dmy(p.get('as_of')) if p.get('as_of') else None,
                  'pmsg':None if present else ('The Latin Church has jurisdiction worldwide; it is not shaded.' if lid=='latin' else 'Present country list not verified.'),
                  'heartland':hl,'hdesc':clean(h.get('description')) if hl else None,'hsrc':h.get('source') if hl else None}
    return out

# ---------- palette (Okabe-Ito hue, lightness adjusted per mode to reach 3:1) ----------
MODES={'light':{'sea':'#e3ebee','land':'#d9cfb9','border':'#a39477'},'dark':{'sea':'#0f131a','land':'#3b414d','border':'#646c7c'}}
def lum(h):
    r,g,b=[int(h[i:i+2],16)/255 for i in(1,3,5)];f=lambda c:c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)
def ratio(a,b):
    la,lb=sorted([lum(a),lum(b)],reverse=True);return (la+0.05)/(lb+0.05)
def hx(r,g,b):return '#%02x%02x%02x'%tuple(max(0,min(255,round(v*255))) for v in(r,g,b))
def adjust(src,bgs,dark,target=3.2):
    r,g,b=[int(src[i:i+2],16)/255 for i in(1,3,5)];h,l,s=colorsys.rgb_to_hls(r,g,b)
    if all(ratio(src,bg)>=target for bg in bgs):return src.lower()
    for i in range(1,200):
        l2=min(1,l+i*0.004) if dark else max(0,l-i*0.004);c=hx(*colorsys.hls_to_rgb(h,l2,s))
        if all(ratio(c,bg)>=target for bg in bgs):return c
    raise SystemExit('no lightness reaches 3:1 for '+src)
def palette():
    P={}
    for mode,m in MODES.items():
        dark=mode=='dark';P[mode]=dict(m)
        for f in FAM_ORDER:
            src=FAMILIES[f]['src'].split(':')[1];fill=adjust(src,[m['land'],m['sea']],dark)
            r,g,b=[int(fill[i:i+2],16)/255 for i in(1,3,5)];h,l,s=colorsys.rgb_to_hls(r,g,b)
            ink=hx(*colorsys.hls_to_rgb(h,min(0.93,l+0.28) if dark else max(0.06,l-0.2),s))
            P[mode]['fill-'+f]=fill;P[mode]['ink-'+f]=ink
    return P
def palette_css(P):
    out=['/* palette:start (generated by tools/build_rites.py; do not edit by hand) */']
    for mode,sel in(('light',':root'),('dark','[data-theme=dark]')):
        out.append(sel+'{'+';'.join('--rm-'+k+':'+v for k,v in P[mode].items())+'}')
    out.append('/* palette:end */');return '\n'.join(out)

# ---------- map markup ----------
def svg_world(geo):
    m=geo['meta'];W,H=int(m['w']),m['h'];K=W/360.0
    defs=''.join('<pattern id="rmp-%s" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" class="rmf-%s"/><rect width="1.6" height="5" class="rmi-%s"/></pattern>'
                 '<pattern id="rmh-%s" width="5" height="5" patternUnits="userSpaceOnUse"><rect width="5" height="5" class="rmf-%s"/><path d="M0 0L5 5M5 0L0 5" class="rmx-%s"/></pattern>'%((f,)*6) for f in FAM_ORDER)
    paths=''.join('<path data-c="%s" d="%s"><title>%s</title></path>'%(c,d,rites_pages.E(geo['names'][c])) for c,d in geo['world'].items())
    loc=''
    for i,ins in enumerate(geo['insets']):
        l0,l1,b0,b1=ins['box'];x0,x1=(l0+180)*K,(l1+180)*K;y0,y1=(84-b1)*K,(84-b0)*K
        loc+='<rect class="rm-locbox" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/><text class="rm-loclbl" x="%.1f" y="%.1f">%s</text>'%(x0-1,y0-1,x1-x0+2,y1-y0+2,x1+2,y0+2 if i!=1 else y1+7,'ABC'[i])
    return ('<svg class="rmap-world" viewBox="0 0 %d %s" role="img" aria-labelledby="rmap-cap" focusable="false"><defs>%s</defs><rect class="rm-sea" width="%d" height="%s"/>'
            '<g class="rm-land">%s</g><g class="rm-loc" aria-hidden="true">%s</g></svg>')%(W,H,defs,W,H,paths,loc)
# country labels in the insets (lon, lat of the label, not a point of interest; no pins)
INSET_LABELS={'lebanon':[('LB',35.8,33.88),('SY',36.45,34.55),('IL',35.25,33.0)],'holy-land':[('IL',34.85,31.25),('JO',35.95,30.6),('EG',34.35,29.75),('LB',35.75,33.38)]}
def svg_insets(geo):
    out=''
    for i,ins in enumerate(geo['insets']):
        paths=''.join('<path data-c="%s" d="%s"><title>%s</title></path>'%(c,d,rites_pages.E(geo['names'][c])) for c,d in ins['paths'].items())
        extra=''
        if ins['outlines'].get('kerala'):
            extra='<path class="rm-region" d="%s"/><text class="rm-regionlbl" x="%.1f" y="%.1f">Kerala</text>'%(ins['outlines']['kerala'],ins['w']*0.53,ins['h']*0.6)
        k=ins['w']/(ins['box'][1]-ins['box'][0])
        for c,lon,lat in INSET_LABELS.get(ins['id'],()):
            assert c in ins['paths'],(ins['id'],c)
            extra+='<text class="rm-clbl" x="%.1f" y="%.1f" text-anchor="middle" aria-hidden="true">%s</text>'%((lon-ins['box'][0])*k,(ins['box'][3]-lat)*k,rites_pages.E(geo['names'][c]))
        cap={'lebanon':'A. Lebanon','holy-land':'B. The Holy Land','kerala':'C. South India: Kerala outlined (shading is by country)'}[ins['id']]
        out+=('<figure class="rmap-inset"><svg viewBox="0 0 %s %s" role="img" aria-label="Inset map: %s" focusable="false"><rect class="rm-sea" width="%s" height="%s"/><g class="rm-land">%s</g>%s</svg><figcaption>%s</figcaption></figure>')%(ins['w'],ins['h'],rites_pages.E(ins['title']),ins['w'],ins['h'],paths,extra,rites_pages.E(cap))
    return '<div class="rmap-insets">'+out+'</div>'

def main():
    raw=json.loads((SRC/'rites-map.json').read_text());shade=json.loads((SRC/'rites-map-shading.json').read_text());geo=json.loads((SRC/'geo.json').read_text())
    names=geo['names'];layers=load_layers(shade,names)
    recs=[record(r,layers) for r in raw['churches']+raw['latin_rites_and_uses']]
    assert len(recs)==31 and len({r['id'] for r in recs})==31
    # family layers: the union of the member Churches' own lists (Eastern families only)
    fams={}
    for f in FAM_ORDER[1:]:
        mem=[r for r in recs if r['kind']=='church' and r['family']==f]
        if len(mem)<2:continue
        fams['fam-'+f]={'family':f,'present':sorted({c for r in mem for c in layers[r['id']]['present']}),'heartland':sorted({c for r in mem for c in layers[r['id']]['heartland']}),
                        'members':[r['id'] for r in mem],'psrc':None,'asof':None,'pmsg':None,'hdesc':'The member Churches\' approximate historical heartlands, combined','hsrc':None}
    layers.update(fams)
    P=palette()
    D={'version':'v19','checked':CHECKED,'families':{f:FAMILIES[f] for f in FAM_ORDER},'records':recs,'layers':layers,'names':names,'palette':P,
       'geo_meta':geo['meta'],'unverified':sorted('%s:%s'%k for k in UNVERIFIED),'dropped':sorted('%s:%s'%k for k in DROP)}
    (ROOT/'data/rites.json').write_text(json.dumps(D,ensure_ascii=False,indent=1)+'\n')
    hub={a['id']:a['name'] for a in json.loads((ROOT/'data/catholic-hub.json').read_text())['authors']}
    lib={w['id']:w for w in json.loads((ROOT/'data/library.json').read_text())['works']}
    saints={s['id']:s['name'] for s in json.loads((ROOT/'data/saints.json').read_text())['saints']}
    for r in recs:
        for x in r['related']:
            ok={'author':(AUTHORS,hub),'work':(WORKS,lib),'saint':(SAINTS,saints)}[x['kind']]
            assert x['id'] in ok[0] and x['id'] in ok[1],('unknown or unapproved cross-link',r['id'],x)
            x['label']=hub.get(x['id']) if x['kind']=='author' else saints.get(x['id']) if x['kind']=='saint' else lib[x['id']]['title']+', '+lib[x['id']]['author']
    B=rites_pages.build(D)
    js={'v':'v19','layers':{k:{'family':v['family'],'present':v['present'],'heartland':v['heartland']} for k,v in layers.items()},'svg':svg_world(geo),'insets':svg_insets(geo)}
    js.update(B)
    (ROOT/'data/rites.js').write_text('window.RITES_DATA='+json.dumps(js,ensure_ascii=False,separators=(',',':'))+';\n')
    css=ROOT/'styles/rites.css';s=css.read_text()
    s2=re.sub(r'/\* palette:start.*?/\* palette:end \*/',lambda m:palette_css(P),s,flags=re.S)
    assert s2!=s or palette_css(P) in s,'styles/rites.css needs the palette markers';css.write_text(s2)
    print('rites: %d records, %d layers, %d unverified shown, %d left out, %d dropped; rites.js %d bytes'%(len(recs),len(layers),len(set(LOG['unv'])),len(set(LOG['nyv'])),len(set(LOG['dropped'])),(ROOT/'data/rites.js').stat().st_size))
if __name__=='__main__':main()
