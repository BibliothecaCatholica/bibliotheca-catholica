"""Unique on-page copy for work pages flagged as thin duplicates in Search Console."""
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLAGGED = [
    "catholic-encyclopedia-advent",
    "catholic-encyclopedia-o-antiphons",
    "book-of-wisdom-douay-rheims",
    "ecclesiasticus-douay-rheims",
    "prudentius-eulalia",
    "jerome-isaiah-prologue",
    "walsh-worlds-debt-catholic-church",
    "butler-eulalia-merida",
    "walsh-saint-teresa",
    "cassidy-molders-of-the-medieval-mind",
    "walsh-high-points-medieval-culture",
    "furfey-mystery-of-iniquity",
    "huber-st-anthony-of-padua",
    "haas-rights-and-wrongs-in-industry",
    "fichter-james-laynez",
]


def words(s):
    return re.findall(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*", s)


class MainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_main = 0
        self.in_skip = 0
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.in_main += 1
        if tag in ("script", "style"):
            self.in_skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.in_skip:
            self.in_skip -= 1
        if tag == "main" and self.in_main:
            self.in_main -= 1

    def handle_data(self, data):
        if self.in_main and not self.in_skip:
            self.chunks.append(data)


class WorkAboutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = json.loads((ROOT / "data/library.json").read_text(encoding="utf-8"))
        cls.by_id = {w["id"]: w for w in cls.lib["works"]}

    def test_flagged_works_have_about_copy(self):
        for wid in FLAGGED:
            w = self.by_id[wid]
            self.assertTrue(w.get("about"), wid)
            about = " ".join(w["about"])
            self.assertGreaterEqual(len(words(about)), 140, wid)
            self.assertNotIn("\u2014", about, wid)

    def test_rendered_flagged_pages_are_no_longer_thin(self):
        for wid in FLAGGED:
            html = (ROOT / "work" / wid / "index.html").read_text(encoding="utf-8")
            p = MainText()
            p.feed(html)
            main = " ".join(p.chunks)
            self.assertIn("About this work", main, wid)
            self.assertIn(self.by_id[wid]["about"][0][:60], main, wid)
            self.assertGreaterEqual(len(words(main)), 300, (wid, len(words(main))))

    def test_excerpts_are_taken_from_the_hosted_file(self):
        for w in self.lib["works"]:
            ex = w.get("excerpt")
            if not ex:
                continue
            edition = next(e for e in w["editions"] if e["id"] == ex["editionId"])
            raw = re.sub(r"\s+", " ", (ROOT / edition["text"]).read_text(encoding="utf-8"))
            for para in re.split(r"\n\s*\n", ex["text"].strip()):
                self.assertIn(re.sub(r"\s+", " ", para), raw, w["id"])
            if "work-excerpt" in (ROOT / "work" / w["id"] / "index.html").read_text(encoding="utf-8"):
                page = (ROOT / "work" / w["id"] / "index.html").read_text(encoding="utf-8")
                self.assertIn("<blockquote", page, w["id"])


    def test_contents_lists_are_not_double_numbered(self):
        """Chapter numerals already live in the labels, so the list itself must not be an <ol>."""
        for w in self.lib["works"]:
            if not w.get("contents"):
                continue
            html = (ROOT / "work" / w["id"] / "index.html").read_text(encoding="utf-8")
            m = __import__("re").search(r'<section class="work-contents">.*?</section>', html, __import__("re").S)
            self.assertIsNotNone(m, w["id"])
            block = m.group(0)
            self.assertIn("<ul>", block, w["id"])
            self.assertNotIn("<ol>", block, w["id"])



if __name__ == "__main__":
    unittest.main()
