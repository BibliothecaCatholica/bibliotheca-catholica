"""Phase A (2026-11), rights rule 10: nothing the site serves may link isidore.co's mobile catalog
(its results list raw get/ files whatever the badge); Markdown notes and tool comments may name it, and no static page may link raw files,
folder listings, or the Calibre viewer.  The app builds get/ URLs only in its two download helpers,
which are gated by the rights badge (tests/rights.test.js)."""
import os,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SKIP_DIRS={'.git','node_modules','dist','.validate','.study-index','.epub-build','.local','.openai','epub-review','__pycache__'}
def _walk_files():
    out=[]
    for dirpath,dirnames,filenames in os.walk(ROOT):
        dirnames[:]=[d for d in sorted(dirnames) if d not in SKIP_DIRS]
        rel_dir=Path(dirpath).relative_to(ROOT)
        for fn in sorted(filenames):
            rel=(rel_dir/fn).as_posix() if rel_dir!=Path('.') else fn
            out.append(rel)
    return out
FILES=_walk_files()
SERVED=[f for f in FILES if not f.startswith(('tests/','docs/','.github/','tools/')) and f.endswith(('.html','.js','.json','.xml','.txt','.css'))
        and not f.startswith(('data/texts/','data/sources/'))]
HTML=[f for f in FILES if f.endswith('.html') and not f.startswith('tools/')]
RAW=re.compile(r'isidore\.co/(calibre/)?(get/|legacy/get/)|/get/(EPUB|PDF|MOBI|AZW3|DJVU|MP3)/|isidore\.co/CalibreLibrary/[^"\'\s<]|#book_id=')
class IsidoreRawLinks(unittest.TestCase):
    def test_no_mobile_catalog_links(self):
        bad=[f for f in SERVED if 'calibre/mobile' in (ROOT/f).read_text(errors='ignore')]
        self.assertEqual(bad,[],'isidore.co/calibre/mobile is linked from: %s'%bad[:10])
    def test_no_search_the_isidore_catalog_label(self):
        bad=[f for f in SERVED if 'Search the isidore.co catalog' in (ROOT/f).read_text(errors='ignore')]
        self.assertEqual(bad,[])
    def test_static_pages_link_no_raw_files(self):
        bad=[(f,m.group(0)) for f in HTML for m in [RAW.search((ROOT/f).read_text(errors='ignore'))] if m]
        self.assertEqual(bad,[])
    def test_app_builds_get_urls_only_in_download_helpers(self):
        for f in ['app.js']+[x for x in FILES if x.startswith('scripts/') and x.endswith('.js')]:
            for line in (ROOT/f).read_text().splitlines():
                if re.search(r"get/|calibre/mobile",line):
                    self.assertRegex(line.strip(),r"^function (dlUrl|isidoreDl)\(",f)
if __name__=='__main__':unittest.main()
