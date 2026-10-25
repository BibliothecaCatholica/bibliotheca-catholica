"""HTML for the /rights and /takedown pages (v16). One source for the app (data/rights-pages.js,
written by tools/build_rights.py) and the static pages (tools/build_static.py). Not legal advice.
Owner decisions still open, kept as visible placeholders: the designated takedown agent (name,
address, email) and whether to register a DMCA agent with the US Copyright Office."""
from html import escape as E
NOT_LEGAL='<p class="notice"><b>This is not legal advice.</b> It explains how this library labels and links books. If you need advice about a particular work, ask a lawyer.</p>'
ORDER=['public_domain_us','open_license','permission_granted','link_only','unknown']
def badge(st,label):
    return '<span class="rights-badge rb-'+st.replace('_','-')+'"><span class="rb-k">Rights:</span> '+E(label)+'</span>'
def rights_html(statuses,counts,checked):
    items=''.join('<li>'+badge(k,statuses[k]['label'])+' <span class="rights-count">('+format(counts.get(k,0),',')+' Index records)</span><br>'+E(statuses[k]['desc'])+
                  (' <b>Download and reader buttons are shown.</b>' if statuses[k]['hostable'] else ' <b>No download or reader buttons.</b>')+'</li>' for k in ORDER)
    return ('<div class="rights-page"><div class="page-head"><div class="eyebrow">Rights &amp; Permissions</div><h1>Rights &amp; Permissions</h1>'
     '<p class="lede">Every record in the Isidore Index, and every edition in the reading room, carries a rights badge. The badge says whether we can offer the book’s files, and why.</p></div>'
     +NOT_LEGAL+
     '<section class="panel policy"><h2>The five badges</h2><ul class="rights-list">'+items+'</ul>'
     '<p>For <b>Link only</b> and <b>Unknown</b> records we link only to the record’s book page on isidore.co, never to its files. Hover over or tap a badge to see the evidence and the date it was checked; a record’s own page shows the same details.</p>'
     '<h2>How the status is decided</h2>'
     '<ul><li><b>Reading-room texts.</b> Each text we host was checked edition by edition before it was added: the specific edition or translation must have been published before 1931, and the evidence is recorded with the edition. These show <b>Public domain (US)</b>.</li>'
     '<li><b>Isidore Index records.</b> Each record was classified on '+E(checked)+' from its catalog year, ISBN, publisher, and an automated match against the NYPL transcription of US copyright renewals. Records presumed in copyright (for example, a 1978 or later edition, an ISBN with no year, a renewed 1931–63 book, or a post-1930 papal or curial text) are <b>Link only</b>.</li>'
     '<li><b>Leads are not decisions.</b> A pre-1931 catalog year, a public-domain source named in the catalog, or “no renewal found” is a lead for a person to check, not proof. Catalog years are often scan or reprint dates, and a modern reprint can add a protected translation, introduction, or notes. Until someone checks the title page and the evidence, these records are <b>Unknown</b>.</li>'
     '<li><b>The only automatic public-domain records</b> in the Index are the same Project Gutenberg texts that our reading room hosts after a rights check.</li>'
     '<li>When in doubt, the status is <b>Unknown</b>. A status changes only with written evidence (a URL, a quotation, or a renewal-record citation) and the date it was checked.</li></ul>'
     '<h2>The checked date</h2><p>Each badge shows when its status was last checked. Copyright status changes over time (each 1 January more US works enter the public domain), and our evidence can improve, so an older date means “as of then”.</p>'
     '<h2>The 1931 rule still applies</h2><p>We host a full text only if that edition was published before 1931 and its rights were checked. Anything later is a link to its source, whatever its badge. A badge of <b>Public domain (US)</b> refers to the United States; the book may not be in the public domain in your country.</p>'
     '<h2>Rights are not recommendations</h2><p>A rights badge says nothing about a book’s content. The <a href="#/policy">Fidelity &amp; Editorial Policy</a> still applies: listing is not endorsement, flagged titles keep their context note, and flagged titles are never featured.</p>'
     '<h2>Corrections and removal</h2><p>If a badge is wrong, or you hold the rights to a work and want a link or a text removed, see <a href="#/takedown">Takedown requests</a>. Data: each record’s <code>rights_status</code>, <code>rights_evidence</code>, and <code>rights_checked</code> are in the <a href="#/data">Open Data</a>.</p>'
     +NOT_LEGAL+'</section></div>')
def takedown_html():
    return ('<div class="rights-page"><div class="page-head"><div class="eyebrow">Rights &amp; Permissions</div><h1>Takedown requests</h1>'
     '<p class="lede">How a rights holder can ask us to remove a text, a link, or a record’s file links.</p></div>'
     +NOT_LEGAL+
     '<section class="panel policy"><h2>What this site holds</h2>'
     '<p>Bibliotheca Catholica hosts only the reading-room texts, each a public-domain edition checked under our pre-1931 rule. The books listed in the Isidore Index are held by isidore.co, not by us: we show their catalog records and link to their book pages. To have a file removed from isidore.co itself, contact isidore.co. We can remove or change our own record, badge, or link.</p>'
     '<h2>Where to send a request</h2>'
     '<p class="placeholder"><b>PLACEHOLDER: designated takedown agent.</b> The name, postal address, and email address of our designated agent will be added here by the site owner. Until then, use the contact address in the <a href="#/policy">Fidelity &amp; Editorial Policy</a> and put “Takedown request” in the subject line.</p>'
     '<h2>What to include</h2><p>A notice is easiest to act on when it has the elements listed in US law (17 U.S.C. § 512(c)(3)):</p><ol>'
     '<li>your physical or electronic signature, as the rights holder or someone authorized to act for them;</li>'
     '<li>the copyrighted work you believe is infringed;</li>'
     '<li>the material on this site, with its page link (for example, an Isidore Index record number or a reading-room address);</li>'
     '<li>your name, postal address, telephone number, and email address;</li>'
     '<li>a statement that you believe in good faith that the use is not authorized by the rights holder, its agent, or the law; and</li>'
     '<li>a statement that the information in your notice is accurate and, under penalty of perjury, that you are authorized to act for the rights holder.</li></ol>'
     '<h2>What happens next</h2><p>We review each request promptly. While we review it, we disable the record’s file links or the hosted text, and we tell you what we changed. If we find we were wrong, we update the badge and its evidence.</p>'
     '<h2>Counter-notices</h2><p>If something you posted or relied on was removed by mistake, you may send a counter-notice with the elements in 17 U.S.C. § 512(g)(3): your signature; the material removed and where it appeared; a statement under penalty of perjury that you believe in good faith it was removed by mistake or misidentification; and your name, address, and telephone number, with consent to the jurisdiction of the federal district court for your address and to accept service from the person who sent the notice.</p>'
     '<h2>Please be accurate</h2><p>Knowingly misrepresenting that material is infringing, or that it was removed by mistake, can create liability (17 U.S.C. § 512(f)).</p>'
     '<p>How badges are decided: <a href="#/rights">Rights &amp; Permissions</a>.</p>'
     +NOT_LEGAL+'</section></div>')
