"""The Magisterium AI referral on the reference and study pages (PROJECT-RULES rule 7, owner-approved placements of
November 19, 2026).

The name and URL come only from `partners.magisterium` in data/affiliates.js, and the disclosure line from its `line`,
so nothing here hard-codes the referral. PAGES is the allowlist (tests/test_affiliate_links.py enforces it): the
referral appears on these pages and nowhere else, never in the header, the footer, author pages, chapter or reading
pages, or the home page. /libraries/ keeps its own wording from #70 (tools/library_desk.py); the four panels here each
say, in one or two sentences, what the tool does for that page's reader, then one link and the one-line disclosure,
below the free reading options. /support/ names the tool in a short note with no referral link, apart from donations.
"""
import html,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];E=html.escape
# route -> where the link appears; 'disclosure' only describes it
PAGES=('libraries','magisterium','councils','summa','study','disclosure')
PANEL_ROUTES=('magisterium','councils','summa','study')
COPY={
 'magisterium':'Magisterium AI searches encyclicals, council documents, the Catechism, and canon law, and answers questions with citations to the passages it used. Use it to find where the Church has taught on a subject, then read the document itself in the links above.',
 'councils':'Magisterium AI can search the decrees and canons of the councils and answer questions with citations, for example what Trent taught on justification. Check each citation against the council texts listed above.',
 'summa':'Magisterium AI answers questions about Catholic teaching in plain language and cites its sources, which can help you find the question you are looking for. Then read St. Thomas himself here, article by article.',
 'study':'Magisterium AI answers questions about Catholic teaching with citations to the Church documents behind each answer. Use it beside the passage search and citations here, and check what it cites against the text.',
}
LINK_TEXT='Try Magisterium AI Pro ↗'
HEADING='Study with Magisterium AI'
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
def link():
    name,url=partner()
    return '<a class="study-partner-link" href="'+E(url)+'" target="_blank" rel="noopener sponsored">'+E(LINK_TEXT)+'</a>'
def panel(route):
    """The panel for one of PANEL_ROUTES: label, heading, the page's sentences, one link, and the disclosure line."""
    assert route in PANEL_ROUTES,route
    return ('<aside class="study-partner" aria-labelledby="study-partner-h"><p class="study-partner-label">A tool we recommend</p>'
            '<h2 id="study-partner-h">'+E(HEADING)+'</h2><p>'+E(COPY[route])+'</p><p class="study-partner-act">'+link()+'</p>'
            +disclosure_line()+'</aside>')
def support_note():
    """/support/: names the tool, with no referral link, after the ways to help and apart from donations."""
    name,_=partner()
    return ('<h2 class="sup-h">Tools we support</h2><p class="sup-tools">We recommend '+E(name)+', a research tool that answers questions about '
            'Catholic teaching with citations to Church documents, on the '
            '<a href="/magisterium/">Church Documents</a>, <a href="/councils/">Ecumenical Councils</a>, <a href="/summa/">Summa</a>, and '
            '<a href="/study/">Study desk</a> pages. A Pro subscription is paid to '+E(name)+' and is not a donation to the library; '
            'if you subscribe through our link, we earn a commission (<a href="/disclosure/">details</a>). '
            'The only way to donate is PayPal, above.</p>')
def disclosure_pages_html(a):
    """The /disclosure/ sentence naming every page that carries the link (a(href,label) builds each link)."""
    names=[('/libraries/','Digital Libraries'),('/magisterium/','Church Documents'),('/councils/','Ecumenical Councils'),('/summa/','Summa Theologiae'),('/study/','Study desk')]
    links=[a(h,t) for h,t in names]
    return ', '.join(links[:-1])+', and '+links[-1]
STUDY_START='<!-- study-partner:start -->';STUDY_END='<!-- study-partner:end -->'
def write_study(path=None):
    """study/index.html is maintained by hand; only the region between the markers is rewritten (idempotent)."""
    p=path or ROOT/'study/index.html'
    if not p.exists():return
    s=p.read_text(encoding='utf-8')
    assert s.count(STUDY_START)==1 and s.count(STUDY_END)==1,'study/index.html needs the study-partner markers'
    s=re.sub(re.escape(STUDY_START)+'.*?'+re.escape(STUDY_END),lambda m:STUDY_START+panel('study')+STUDY_END,s,flags=re.S)
    p.write_text(s,encoding='utf-8')
