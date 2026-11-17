"""tools/transcribe_scan.py: the general single-scan transcription tool (November 16, 2026), and every record it made."""
import hashlib, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import transcribe_scan as T  # noqa: E402
from rights_rule import pd_by_date  # noqa: E402

V = {'god': 9000, 'grad': 3, 'universal': 1340, 'unconscious': 80, 'found': 5000, 'born': 900, 'well': 8000, 'our': 20000,
     'burns': 40, 'class': 300}
RECORDS = [json.loads(p.read_text()) for p in (ROOT / 'data/sources').glob('*.json')]
RECORDS = [r for r in RECORDS if r.get('kind') == 'ocr-transcription' and r.get('method', '').startswith('tools/transcribe_scan.py')]


class Repair(unittest.TestCase):
    def test_repairs_only_a_clearly_commoner_known_word(self):
        self.assertEqual(T.repair('Grod', V)[0], 'God')            # 'God' is far commoner than 'Grad'
        self.assertEqual(T.repair('tmiversal,', V)[0], 'universal,')
        self.assertEqual(T.repair('imconscious', V)[0], 'unconscious')
        self.assertEqual(T.repair('foimd', V)[0], 'found')

    def test_semicolon_read_as_j(self):
        import re
        self.assertEqual(re.sub(r'(?<=[A-Za-z]) j(?= [a-z])', ';', 'most sinister of all contradictions j when we'),
                         'most sinister of all contradictions; when we')

    def test_never_guesses(self):
        self.assertEqual(T.repair('oiu*', V), ('oiu*', 'unknown'))  # too short to repair: flagged, kept as printed
        self.assertEqual(T.repair('babjdsh', V), ('babjdsh', 'unknown'))
        self.assertEqual(T.repair('well', V), ('well', None))
        self.assertEqual(T.repair('1912', V), ('1912', None))

    def test_double_escaped_ocr_is_unescaped(self):
        import xml.etree.ElementTree as ET
        o = ET.fromstring('<OBJECT><PARAGRAPH><LINE><WORD coords="1,20,9,2">&amp;quot;Sir,</WORD></LINE></PARAGRAPH></OBJECT>')
        self.assertEqual(T.page_lines(o)[0]['text'], '"Sir,')

    def test_running_head_and_page_number_dropped(self):
        L = lambda t, y: {'x': 100, 'y': y, 'h': 30, 'text': t, 'paraStart': False, 'para': 0}
        page = [L('19', 150), L('SIMPLICITY AND TOLSTOY', 300), L('universe topsy-turvy, and makes it', 450), L('the end.', 900), L('20', 2200)]
        self.assertEqual([l['text'] for l in T.body(page, 2600, {'simplicityandtolstoy'})], ['universe topsy-turvy, and makes it', 'the end.'])
        noise = [L('U', 500), L('•*v', 600), L('real words here', 700)]
        self.assertEqual([l['text'] for l in T.body(noise, 2600, set())], ['real words here'])


class Layout(unittest.TestCase):
    L = staticmethod(lambda t, y, h=50: {'x': 100, 'y': y, 'h': h, 'text': t, 'paraStart': False, 'para': 0})

    def test_footnotes_leave_the_page_body(self):
        body = [self.L('line %d of the text' % i, 300 + 85 * i) for i in range(20)]
        page = body + [self.L('* “The Humanism of Irving Babbitt,” The Forum.', 2000, 40), self.L('5 Moral., X, xvi, quoted', 2050, 40),
                       self.L('Cassian, Migne, XLIX, 774.', 2100, 50)]
        kept, notes = T.split_notes(page, 2600)
        self.assertEqual(kept, body)
        self.assertEqual([n[0][:3] for n in notes], ['* “', '5 M'])
        self.assertEqual(notes[1][-1], 'Cassian, Migne, XLIX, 774.')  # a note's second line stays with it
        self.assertEqual(T.split_notes(body, 2600), (body, []))
        dotted = body + [self.L('10. Cf. Dark Night, I, xiv, 2.', 2300, 40), self.L('11 Dark Night of the Soul, II, vi, 2.', 2350, 40)]
        self.assertEqual(len(T.split_notes(dotted, 2600)[1]), 2)  # a number followed by a full stop is a note mark too

    def test_library_stamp_dropped_but_running_heads_kept(self):
        pages = [(3000, [self.L('THE THING', 100), self.L('text', 300), self.L('MARIN COUNTY FREE LIBRARY', 500)]) for _ in range(4)]
        stamps = T.library_stamps(pages, {'thething'})
        self.assertTrue(T.is_stamp('MARIN COUNTTY FREE LIBRARY', stamps))  # an OCR variant of the same stamp
        self.assertFalse(T.is_stamp('THE THING', stamps))


class Records(unittest.TestCase):
    def test_every_transcription_is_pinned_flagged_and_dated(self):
        for r in RECORDS:
            raw = (ROOT / r['text']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), r['sha256'], r['id'])
            text = raw.decode('utf-8')
            self.assertTrue(text.rstrip().endswith(T.END), r['id'])
            self.assertIn('Not a manual proofread.', text, r['id'])
            self.assertIn('*** START OF THE TRANSCRIPTION ***', text, r['id'])
            self.assertGreaterEqual(r['readRate'], 0.995, r['id'])  # unread words stay flagged; this is the gate
            self.assertEqual(r['flaggedBlocks'], len(r['flagged']), r['id'])
            self.assertEqual(r['corrections'], len(r['correctionList']), r['id'])
            self.assertEqual(r['rightsBasis'], 'pd-date', r['id'])
            for v in r['volumes']:
                self.assertTrue(pd_by_date(v['year']), r['id'])
                self.assertEqual(v['url'], 'https://archive.org/details/' + v['identifier'])
                self.assertRegex(v['ocrSha256'], r'^[0-9a-f]{64}$')


if __name__ == '__main__':
    unittest.main()
