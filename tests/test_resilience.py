"""Static fallbacks, publication identity, and safe source URL contracts."""
import hashlib,ipaddress,json,re,sys,unittest
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'));import build_info
class Resilience(unittest.TestCase):
    def test_template_forms_and_fallbacks(self):
        s=(ROOT/'index.html').read_text()
        self.assertRegex(s,r'<form[^>]+id="site-search"[^>]+action="/search/"[^>]+method="get"')
        self.assertIn('name="lookup"',s);self.assertIn('type="submit" class="search-submit"',s)
        self.assertIn('aria-controls="suggest"',s);self.assertIn('role="alert" hidden',s)
        self.assertLess(s.index('scripts/boot.js'),s.index('<body>'))
        self.assertIn('strict-origin-when-cross-origin',s)
        self.assertIn('Official source repository',s)
        directory=(ROOT/'search/index.html').read_text()
        self.assertIn('browser’s Find',directory);self.assertIn('/work/confessions/',directory);self.assertIn('/author/thomas-aquinas/',directory)
    def test_every_content_page_has_a_date_and_matching_build(self):
        info=json.loads((ROOT/'build.json').read_text());hub=json.loads((ROOT/'data/catholic-hub.json').read_text())
        self.assertEqual(info['dataSnapshot'],hub['generated']);self.assertRegex(info['id'],r'^bc-[a-f0-9]{12}$')
        files=['index.html']+(ROOT/'docs/static-pages.txt').read_text().split()
        for f in files:
            s=(ROOT/f).read_text();self.assertIn('<span id="gen">'+hub['generated']+'</span>',s,f)
            self.assertIn('<span id="build-id">'+info['id']+'</span>',s,f)
        self.assertEqual(info['sha256']['app.js'],hashlib.sha256((ROOT/'app.js').read_bytes()).hexdigest())
        s=(ROOT/'index.html').read_text()
        self.assertEqual(info['sha256']['index.template'],hashlib.sha256(build_info.normalized_template(s).encode()).hexdigest())
    def test_home_metadata_and_scope_agree(self):
        s=(ROOT/'index.html').read_text();copy=json.loads((ROOT/'data/site-copy.js').read_text()[len('window.SITE_COPY='):].strip().rstrip(';'))
        title=re.search(r'<title>(.*?)</title>',s)[1]
        self.assertEqual(title,copy['homeTitle'])
        for k in ('og:title','twitter:title'):self.assertIn('content="'+title+'"',re.search(r'<meta (?:name|property)="'+k+'"[^>]+>',s)[0])
        self.assertNotIn('master library',copy['home'].lower());self.assertNotIn('master library',copy['about'].lower())
    def test_source_fields_have_safe_schemes(self):
        hub=json.loads((ROOT/'data/catholic-hub.json').read_text());lib=json.loads((ROOT/'data/library.json').read_text())
        urls=[e['source'] for w in lib['works'] for e in w['editions']]
        urls += [x['url'] for a in hub['authors'] for x in a.get('links',[])+a.get('works',[]) if x.get('url')]
        urls += [r['url'] for r in hub['resources']]
        for url in urls:
            p=urlsplit(url);self.assertIn(p.scheme,('http','https'),url);self.assertTrue(p.hostname,url)
            self.assertFalse(p.username or p.password,url)
            self.assertNotIn(p.hostname.lower(),('localhost','localhost.localdomain'),url)
            try:ip=ipaddress.ip_address(p.hostname)
            except ValueError:continue
            self.assertTrue(ip.is_global,url)
