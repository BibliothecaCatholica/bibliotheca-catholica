"""The Magisterium AI referral (PROJECT-RULES rule 7).

The name and URL come only from `partners.magisterium` in data/affiliates.js, and the disclosure line from
its `line`, so nothing here hard-codes the referral.

Owner-approved placements of 19 November 2026 remain: /libraries/ (its own wording in tools/library_desk.py),
/magisterium/, /councils/, the /summa/ landing page, /study/, and /disclosure/. Owner-approved draft of
21 November 2026 adds Ask blocks on the home page, /scripture/, /saints/ (the index only), /doctors/, and
/prayers/; Ask-about-this-book questions on selected work pages; Ask buttons beside vatican.va links on
Church Documents; and /about/magisterium-ai/. The Advent plan and data/advent-2026.json are left untouched
until the freeze ends on 24 December 2026. The referral never appears in the header, the footer, author
pages, or chapter or reading pages.

/support/ names the tool in a short note with no referral link, apart from donations.
"""
import html, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];E=html.escape
# route -> where the link appears; 'disclosure' only describes it
PAGES=('libraries','magisterium','councils','summa','study','disclosure','scripture','saints','doctors','prayers','about/magisterium-ai')
PANEL_ROUTES=('magisterium','councils','summa','study')
ASK_ROUTES=('home','scripture','saints','doctors','prayers')
BOOK_WORKS=('confessions','orthodoxy','dei-verbum','lumen-gentium','sacrosanctum-concilium','gaudium-spes','council-of-trent')
COPY={
 'magisterium':'Magisterium AI searches encyclicals, council documents, the Catechism, and canon law, and answers questions with citations to the passages it used. Use it to find where the Church has taught on a subject, then read the document itself in the links above.',
 'councils':'Magisterium AI can search the decrees and canons of the councils and answer questions with citations, for example what Trent taught on justification. Check each citation against the council texts listed above.',
 'summa':'Magisterium AI answers questions about Catholic teaching in plain language and cites its sources, which can help you find the question you are looking for. Then read St. Thomas himself here, article by article.',
 'study':'Magisterium AI answers questions about Catholic teaching with citations to the Church documents behind each answer. Use it beside the passage search and citations here, and check what it cites against the text.',
}
# Suggested questions, written in our own words. Prefilled ?q= links do not work, so the questions stay on our page.
QUESTIONS={
 'home':(
  'What does the Church teach about the relationship between Scripture and Tradition?',
  'How does the Catechism explain prayer, and which passages does it cite?',
  'Where can I start if I want to read the Church Fathers on the Incarnation?',
 ),
 'scripture':(
  'What is the Catholic sense of this passage, and which Church documents discuss it?',
  'How does Dei Verbum describe the relationship between Scripture and Tradition?',
  'Which Psalms does the Church use most often in the Liturgy of the Hours?',
 ),
 'saints':(
  'Who was St. Francis de Sales, and what did he write?',
  'What does the Church teach about the communion of saints?',
  'How does the Church decide the rank of a feast, memorial, or solemnity?',
 ),
 'doctors':(
  'What does it mean for the Church to name someone a Doctor of the Church?',
  'What is St. Thomas Aquinas\'s teaching on the Eucharist in the Summa Theologiae?',
  'What did St. Teresa of Avila write about prayer, and where should a reader begin?',
 ),
 'prayers':(
  'How does the Church teach us to pray the Rosary, and what are the mysteries?',
  'What is the difference between liturgical prayer and private devotion?',
  'Where does the Catechism discuss the Lord\'s Prayer, petition by petition?',
 ),
 'magisterium':(
  'What does Pascendi teach about Modernism?',
  'Where does Dei Verbum talk about Scripture and Tradition?',
  'What does the Catechism say about the Eucharist, and which earlier documents does it cite?',
  'How should a reader check a citation from an AI tool against vatican.va?',
 ),
 'councils':(
  'What did the Council of Nicaea define about the Son?',
  'How did the Council of Trent describe justification?',
  'What is Lumen Gentium\'s teaching on the Church?',
  'Where does Sacrosanctum Concilium discuss the place of Scripture in the liturgy?',
 ),
 'summa':(
  'How does Thomas Aquinas explain the Eucharist in the Summa Theologiae?',
  'Where does the Summa treat the existence of God, and how does the argument proceed?',
  'What does Aquinas say about law, including the natural law?',
  'How does the Summa describe charity, and how is it distinct from faith?',
 ),
 'study':(
  'How can I trace a short quotation to the Church document it comes from?',
  'What does the Church teach about conscience, and which documents should I read first?',
  'How should I read a council canon alongside the chapter that introduces it?',
 ),
}
BOOK_QUESTIONS={
 'confessions':(
  'What does Augustine mean when he says our heart is restless until it rests in God?',
  'How does Augustine describe his conversion in Book VIII of the Confessions?',
  'What does the Confessions teach about memory, time, and the inner life?',
  'How does Augustine read the opening of Genesis in the later books?',
 ),
 'orthodoxy':(
  'What does Chesterton mean by the romance of orthodoxy?',
  'How does Orthodoxy argue that wonder and Christian dogma belong together?',
  'What is Chesterton\'s case against reshaping the truth to suit the age?',
  'How does he describe the Church as a truth-telling thing?',
 ),
 'dei-verbum':(
  'What does Dei Verbum teach about divine revelation?',
  'How does the constitution describe the relationship between Scripture and Tradition?',
  'What does Dei Verbum say about the role of the Magisterium in interpreting Scripture?',
  'How should a Catholic read Scripture according to this document?',
 ),
 'lumen-gentium':(
  'What does Lumen Gentium teach about the mystery of the Church?',
  'How does the constitution describe the role of the laity?',
  'What does Lumen Gentium say about the Blessed Virgin Mary and the Church?',
  'How does it present the college of bishops in relation to the Pope?',
 ),
 'sacrosanctum-concilium':(
  'What does Sacrosanctum Concilium teach about the liturgy as the work of Christ and the Church?',
  'How does the constitution describe the place of Scripture in the liturgy?',
  'What does it say about the full, conscious, and active participation of the faithful?',
  'How does it treat the use of Latin and the vernacular?',
 ),
 'gaudium-spes':(
  'What does Gaudium et Spes say about the Church\'s relationship to the modern world?',
  'How does the constitution describe the dignity of the human person?',
  'What does it teach about marriage and the family?',
  'How does it present the Church\'s role in the political community?',
 ),
 'council-of-trent':(
  'How did the Council of Trent describe justification?',
  'What does Trent teach about the canon of Scripture and the authority of Tradition?',
  'How does Trent present the Eucharist, including transubstantiation?',
  'What did the council say about the number and nature of the sacraments?',
 ),
}
BOOK_TITLES={
 'confessions':'Confessions',
 'orthodoxy':'Orthodoxy',
 'dei-verbum':'Dei Verbum',
 'lumen-gentium':'Lumen Gentium',
 'sacrosanctum-concilium':'Sacrosanctum Concilium',
 'gaudium-spes':'Gaudium et Spes',
 'council-of-trent':'the Canons and Decrees of the Council of Trent',
}
ASK_COPY={
 'home':'Magisterium AI answers questions about Catholic teaching with citations to Church documents. Use it as a finding aid, then read the sources themselves in this library or on vatican.va.',
 'scripture':'Magisterium AI can help you find the Catholic sense of a passage and the documents that discuss it. The official lectionary text of the day is on the USCCB or Universalis, linked from Prayers. Check each citation against the biblical text and the Church documents it names.',
 'saints':'Magisterium AI can answer questions about the saints and the Church\'s calendar, with citations. Treat feast dates as a starting point and check them against Vatican News or the calendar in this guide. The calendar pages themselves stay facts-only.',
 'doctors':'Magisterium AI can help you find what a Doctor of the Church taught, and where. Then read the writer in the editions linked from this page, and check each citation against the text.',
 'prayers':'Magisterium AI can point you to the Church\'s teaching on prayer and to the texts behind familiar devotions. Check what it cites against the prayers here and against the documents on vatican.va.',
}
LINK_TEXT='Try Magisterium AI Pro ↗'
ASK_LINK_TEXT='Ask Magisterium AI ↗'
ASK_BTN_TEXT='Ask ↗'
HEADING='Study with Magisterium AI'
ASK_HEADING='Ask Magisterium AI'
BOOK_HEADING='Ask about this book'
QS_INTRO='Questions to ask Magisterium AI. Type or paste one into the tool; the question is not filled in for you.'
INDEPENDENT='Bibliotheca Catholica is an independent project. It is not endorsed by Magisterium AI or by the Catholic Church.'
WHY_HREF='/about/magisterium-ai/'
WHY_LABEL='Why we use Magisterium AI'
def _affiliates():return (ROOT/'data'/'affiliates.js').read_text(encoding='utf-8')
def partner():
    """(name, url) of partners.magisterium in data/affiliates.js."""
    s=_affiliates();block=s[s.index('partners'):]
    m=re.search(r"magisterium:\s*\{\s*name:\s*'([^']+)',\s*url:\s*'(https://[^']+)'",block)
    assert m,'data/affiliates.js must define partners.magisterium with a name and an https url'
    return m.group(1),m.group(2)
def disclosure_line():
    """The one-line FTC disclosure (rule 7), the same markup as app.js discl() and build_print_editions."""
    m=re.search(r"\bline:\s*'([^']+)'",_affiliates());assert m
    return '<p class="disclosure small">'+E(m.group(1))+' <a href="/disclosure/">Details</a>.</p>'
def link(text=None):
    name,url=partner()
    return '<a class="study-partner-link" href="'+E(url)+'" target="_blank" rel="noopener sponsored">'+(E(text) if text else E(LINK_TEXT))+'</a>'
def ask_button():
    """A compact Ask control for use beside a vatican.va link. The page already carries the disclosure line."""
    _,url=partner()
    return ('<a class="study-ask-btn" href="'+E(url)+'" target="_blank" rel="noopener sponsored" '
            'aria-label="Ask Magisterium AI about this document">'+E(ASK_BTN_TEXT)+'</a>')
def is_vatican_url(url):
    return bool(re.match(r'https?://(?:[a-z0-9-]+\.)*vatican\.va(?:/|$)', (url or ''), re.I))
def _questions(items):
    lis=''.join('<li>'+E(q)+'</li>' for q in items)
    return ('<p class="study-partner-qs-intro">'+E(QS_INTRO)+'</p>'
            '<ul class="study-partner-qs">'+lis+'</ul>')
def _note():
    return ('<p class="small muted study-partner-note">'+E(INDEPENDENT)+' '
            '<a href="'+E(WHY_HREF)+'">'+E(WHY_LABEL)+'</a>.</p>')
def panel(route):
    """The panel for one of PANEL_ROUTES: label, heading, the page's sentences, questions, one link, and the disclosure line."""
    assert route in PANEL_ROUTES,route
    qs=_questions(QUESTIONS[route]) if route in QUESTIONS else ''
    return ('<aside class="study-partner" aria-labelledby="study-partner-h"><p class="study-partner-label">A tool we recommend</p>'
            '<h2 id="study-partner-h">'+E(HEADING)+'</h2><p>'+E(COPY[route])+'</p>'+qs
            +'<p class="study-partner-act">'+link()+'</p>'+_note()+disclosure_line()+'</aside>')
def ask_block(route, disclosure=True, heading_id=None):
    """A compact Ask Magisterium AI block for a high-traffic section page or the home page."""
    assert route in ASK_ROUTES,route
    hid=heading_id or ('study-ask-h-'+route)
    qs=_questions(QUESTIONS[route])
    html=('<aside class="study-partner study-ask" aria-labelledby="'+E(hid)+'">'
          '<p class="study-partner-label">A tool we recommend</p>'
          '<h2 id="'+E(hid)+'">'+E(ASK_HEADING)+'</h2>'
          '<p>'+E(ASK_COPY[route])+'</p>'+qs
          +'<p class="study-partner-act">'+link(ASK_LINK_TEXT)+'</p>'+_note()
          +(disclosure_line() if disclosure else '')+'</aside>')
    return html
def ask_blocks():
    """route -> HTML for the Ask blocks on home and the section pages that do not already have a study panel."""
    return {r:ask_block(r) for r in ASK_ROUTES}
def _print_disclosure_works():
    p=ROOT/'data'/'print-editions.json'
    if not p.exists():return set()
    pe=json.loads(p.read_text(encoding='utf-8'))
    return {wid for wid,v in (pe.get('works') or {}).items() if 'class="disclosure ' in (v.get('html') or '') or 'class="disclosure"' in (v.get('html') or '')}
def book_panel(wid, disclosure=None):
    """Ask-about-this-book questions on a major work page."""
    assert wid in BOOK_QUESTIONS,wid
    if disclosure is None:disclosure=wid not in _print_disclosure_works()
    title=BOOK_TITLES[wid]
    hid='study-book-h-'+wid
    return ('<aside class="study-partner study-ask-book" aria-labelledby="'+E(hid)+'">'
            '<p class="study-partner-label">A tool we recommend</p>'
            '<h2 id="'+E(hid)+'">'+E(BOOK_HEADING)+'</h2>'
            '<p>Questions to ask Magisterium AI while you read <cite>'+E(title)+'</cite>. '
            'Type or paste one into the tool; the question is not filled in for you.</p>'
            '<ul class="study-partner-qs">'+''.join('<li>'+E(q)+'</li>' for q in BOOK_QUESTIONS[wid])+'</ul>'
            +'<p class="study-partner-act">'+link(ASK_LINK_TEXT)+'</p>'+_note()
            +(disclosure_line() if disclosure else '')+'</aside>')
def book_panels():
    """work id -> HTML, with a disclosure line only when the work page does not already have one."""
    have=_print_disclosure_works()
    return {wid:book_panel(wid, disclosure=wid not in have) for wid in BOOK_WORKS}
def why_page():
    """Short 'Why we use Magisterium AI' page at /about/magisterium-ai/."""
    name,url=partner()
    return (
        '<div class="page-head"><div class="eyebrow">The library</div>'
        '<h1>Why we use Magisterium AI</h1>'
        '<p class="lede">A short note on a research tool we recommend, and how the referral works.</p></div>'
        '<section class="panel policy">'
        '<h2>What it is</h2>'
        '<p>'+E(name)+' is a research tool that answers questions about Catholic teaching and cites the Church documents it used. '
        'We use it as a finding aid when we want to locate a passage, a feast, or a citation quickly.</p>'
        '<h2>Why we link it</h2>'
        '<p>We recommend it because we use it and find it useful, not because of the commission. '
        'The questions on our pages are ours. Type or paste one into the tool; we do not pre-fill the question for you. '
        'A referral link may include a discount on a paid subscription.</p>'
        '<p class="study-partner-act">'+link(ASK_LINK_TEXT)+'</p>'
        '<h2>Independence</h2>'
        '<p>'+E(INDEPENDENT)+' Participation in an affiliate program is not an endorsement, sponsorship, or approval by '
        +E(name)+' or by Longbeard Inc. We are not an official voice of the Church.</p>'
        '<h2>Check the sources</h2>'
        '<p>Answers from '+E(name)+' are generated by a machine. They should be checked against the sources they cite, '
        'preferably on <a href="https://www.vatican.va/content/vatican/en.html" target="_blank" rel="noopener">vatican.va</a> '
        'or in a public-domain edition in this library. They are not official Church teaching simply by appearing here. '
        'Free reading in this library always comes first. We host only public-domain or openly licensed texts.</p>'
        '<h2>Affiliate disclosure</h2>'
        '<p>Bibliotheca Catholica is a participant in the Magisterium AI affiliate program. Links to Magisterium AI on this site, '
        'including Ask Magisterium AI buttons, use our referral address, '+E(url)+'. If you take out a paid Magisterium AI subscription '
        'after following one of those links, you may receive a discount (the program currently advertises 25% off), and '
        'Bibliotheca Catholica may receive a commission (currently 10% of qualifying subscription revenue). Those rates are set by '
        'Magisterium AI and may change. There is no extra cost to you. We recommend Magisterium AI because we use it and find it useful, '
        'not because of the commission. See also the <a href="/disclosure/">affiliate disclosure</a> for Bookshop.org, TAN Books, and Magisterium AI.</p>'
        +disclosure_line()+
        '</section>'
    )
def support_note():
    """/support/: names the tool, with no referral link, after the ways to help and apart from donations."""
    name,_=partner()
    return ('<h2 class="sup-h">Tools we support</h2><p class="sup-tools">We recommend '+E(name)+', a research tool that answers questions about '
            'Catholic teaching with citations to Church documents, on the '
            '<a href="/magisterium/">Church Documents</a>, <a href="/councils/">Ecumenical Councils</a>, <a href="/summa/">Summa</a>, and '
            '<a href="/study/">Study desk</a> pages, and in short Ask prompts on other section pages. A Pro subscription is paid to '+E(name)+' and is not a donation to the library; '
            'if you subscribe through our link, we earn a commission (<a href="/disclosure/">details</a>). '
            'The only way to donate is PayPal, above. '+a_why()+'</p>')
def a_why():
    return '<a href="'+E(WHY_HREF)+'">'+E(WHY_LABEL)+'</a>.'
def disclosure_pages_html(a):
    """The /disclosure/ sentence naming every page that carries the link (a(href,label) builds each link)."""
    names=[('/', 'the home page'),('/scripture/','Sacred Scripture'),('/magisterium/','Church Documents'),('/councils/','Ecumenical Councils'),
           ('/summa/','Summa Theologiae'),('/study/','Study desk'),('/saints/','Saints'),('/doctors/','Doctors of the Church'),
           ('/prayers/','Prayers & Devotions'),('/libraries/','Digital Libraries'),(WHY_HREF, WHY_LABEL)]
    links=[a(h,t) for h,t in names]
    works='selected work pages, including '+a('/work/confessions/','Confessions')+', '+a('/work/orthodoxy/','Orthodoxy')+', and the hosted council documents'
    return ', '.join(links)+', and '+works
def placement_files():
    """Static HTML paths that may carry the referral URL (the allowlist test uses this)."""
    files={r+'/index.html' for r in PAGES}
    files.add('index.html')  # the home page
    files.update('work/'+wid+'/index.html' for wid in BOOK_WORKS)
    return files
STUDY_START='<!-- study-partner:start -->';STUDY_END='<!-- study-partner:end -->'
def write_study(path=None):
    """study/index.html is maintained by hand; only the region between the markers is rewritten (idempotent)."""
    p=path or ROOT/'study/index.html'
    if not p.exists():return
    s=p.read_text(encoding='utf-8')
    assert s.count(STUDY_START)==1 and s.count(STUDY_END)==1,'study/index.html needs the study-partner markers'
    s=re.sub(re.escape(STUDY_START)+'.*?'+re.escape(STUDY_END),lambda m:STUDY_START+panel('study')+STUDY_END,s,flags=re.S)
    p.write_text(s,encoding='utf-8')
