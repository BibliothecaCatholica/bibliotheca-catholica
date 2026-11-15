"""tools/draft_text_map.py reproduces hand-made chapter maps from the texts' own headings (agent efficiency)."""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import draft_text_map as D  # noqa: E402
import text_pages as TP  # noqa: E402


def heads(parts):
    return [tuple(' '.join(x.split()) for x in (p[3] if isinstance(p[3], tuple) else (p[3],))) for p in parts]


class DraftTextMap(unittest.TestCase):
    def test_drafts_match_hand_maps(self):
        for wid in ('orthodoxy', 'heretics', 'ball-and-cross', 'man-thursday', 'chesterton-francis', 'grammar-assent',
                    'apologia', 'virgin-saints-and-martyrs', 'incredulity-father-brown'):
            spec, items = D.draft(wid)
            self.assertEqual(heads(spec['parts']), heads(TP.WORKS[wid]['parts']), wid)
            self.assertEqual(len(items), len(TP.WORKS[wid]['parts']), wid)

    def test_render_is_a_works_entry(self):
        spec, _ = D.draft('orthodoxy')
        ns = {}
        exec('W={' + D.render('orthodoxy', spec) + '}', ns)
        self.assertEqual(ns['W']['orthodoxy']['edition'], 'pg-130')
        self.assertTrue(all(len(p[0]) <= 60 for p in ns['W']['orthodoxy']['parts']))


if __name__ == '__main__':
    unittest.main()
