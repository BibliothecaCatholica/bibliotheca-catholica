"""Footer social links (X and Bluesky) on every pre-rendered page, and Organization sameAs (steering B, 2026-11-03)."""
import json,re,unittest,pathlib
ROOT=pathlib.Path(__file__).resolve().parent.parent
X='https://x.com/BiblioCatholica';BS='https://bsky.app/profile/bibliothecacatholica.com'
PAGES=[p for p in ROOT.glob('**/index.html') if 'node_modules' not in p.parts and p.parts[len(ROOT.parts)]!='docs']
def footer(s):
    m=re.search(r'<footer class="footer">.*?</footer>',s,re.S);return m.group(0) if m else ''
class SocialLinks(unittest.TestCase):
    def test_every_page_footer_links_both_accounts(self):
        self.assertGreater(len(PAGES),700)
        for p in PAGES:
            f=footer(p.read_text())
            with self.subTest(page=str(p.relative_to(ROOT))):
                self.assertIn('href="%s" target="_blank" rel="noopener"'%X,f)
                self.assertIn('href="%s" target="_blank" rel="noopener"'%BS,f)
                self.assertIn('independent project, not official accounts of the Catholic Church',f)
    def test_no_official_church_wording(self):
        f=footer((ROOT/'index.html').read_text())
        line=re.search(r'<p class="small social-links">.*?</p>',f,re.S).group(0)
        self.assertNotRegex(line.replace('not official accounts of the Catholic Church',''),r'(?i)official|vatican|endorsed')
        self.assertNotIn('\u2014',line)
    def test_same_as(self):
        s=(ROOT/'index.html').read_text()
        orgs=[j for j in (json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)) for j in (j if isinstance(j,list) else j.get('@graph',[j]))]
        org=[o for o in orgs if o.get('@type')=='Organization']
        self.assertEqual(len(org),1);self.assertEqual(org[0]['sameAs'],['https://github.com/BibliothecaCatholica',X,BS])
if __name__=='__main__':unittest.main()
