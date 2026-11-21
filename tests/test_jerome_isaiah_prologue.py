"""Jerome, Commentary on Isaiah, prologue (Latin, PL 24 collation, 21 November 2026)."""
import hashlib, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import notices as N  # noqa: E402

LINE = "ignoratio Scripturarum, ignoratio Christi est"
SRC_URL = "https://mlat.uzh.ch/?text=7170"


class JeromeIsaiahPrologue(unittest.TestCase):
    def setUp(self):
        self.lib = json.loads((ROOT / "data/library.json").read_text())
        self.work = next(w for w in self.lib["works"] if w["id"] == "jerome-isaiah-prologue")
        self.ed = self.work["editions"][0]
        self.rec = json.loads((ROOT / "data/sources" / (self.ed["id"] + ".json")).read_text())
        self.text = (ROOT / self.ed["text"]).read_text(encoding="utf-8")

    def test_scope_is_the_latin_prologue_only(self):
        self.assertEqual(self.work["authorId"], "jerome")
        self.assertEqual(self.ed["language"], "Latin")
        self.assertEqual(self.ed["rightsBasis"], "pd-date")
        self.assertEqual(self.ed["source"], SRC_URL)
        self.assertEqual(self.rec["kind"], "collation")
        self.assertEqual(self.rec["collation"]["agreement"], 1.0)
        self.assertEqual(self.rec["collation"]["wordVariants"], [])
        self.assertIn("prologue only", self.ed["note"].lower())
        self.assertIn("no english translation", self.ed["note"].lower())
        self.assertNotIn("LIBER PRIMUS", self.text.split("*** START OF THE HOSTED TEXT ***", 1)[1])

    def test_checksum_and_the_media_line(self):
        raw = (ROOT / self.ed["text"]).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.ed["sha256"])
        self.assertEqual(self.ed["sha256"], self.rec["sha256"])
        self.assertIn(LINE, self.text)
        self.assertIn("*** START OF THE HOSTED TEXT ***", self.text)
        self.assertTrue(self.text.rstrip().endswith("***"))

    def test_notice_is_corpus_corporum_not_a_false_standard_ebooks_label(self):
        self.assertEqual(N.source_kind(self.ed["source"]), "mlat")
        n = N.notice_for(self.ed["source"])
        self.assertIn("Corpus Corporum", n)
        self.assertIn("Patrologia Latina", n)
        self.assertNotIn("Standard Ebooks edition", n)
        self.assertNotIn("Project Gutenberg\u2122 License", n)
        self.assertNotIn("\u2014", n)

    def test_stable_media_url_is_a_path(self):
        self.assertIn("/work/jerome-isaiah-prologue/ignoratio-scripturarum/", self.ed["note"])
        page = ROOT / "work/jerome-isaiah-prologue/ignoratio-scripturarum/index.html"
        if page.exists():
            html = page.read_text(encoding="utf-8")
            self.assertIn(LINE, html)
            self.assertIn('rel="canonical" href="https://bibliothecacatholica.com/work/jerome-isaiah-prologue/ignoratio-scripturarum/"', html)
            self.assertNotIn("Standard Ebooks", html)


if __name__ == "__main__":
    unittest.main()
