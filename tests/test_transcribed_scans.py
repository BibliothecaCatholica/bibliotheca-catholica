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

    def test_never_guesses(self):
        self.assertEqual(T.repair('oiu*', V), ('oiu*', 'unknown'))  # too short to repair: flagged, kept as printed
        self.assertEqual(T.repair('babjdsh', V), ('babjdsh', 'unknown'))
        self.assertEqual(T.repair('well', V), ('well', None))
        self.assertEqual(T.repair('1912', V), ('1912', None))

    def test_running_head_and_page_number_dropped(self):
        L = lambda t, y: {'x': 100, 'y': y, 'h': 30, 'text': t, 'paraStart': False, 'para': 0}
        page = [L('19', 150), L('SIMPLICITY AND TOLSTOY', 300), L('universe topsy-turvy, and makes it', 450), L('the end.', 900), L('20', 2200)]
        self.assertEqual([l['text'] for l in T.body(page, 2600, {'simplicityandtolstoy'})], ['universe topsy-turvy, and makes it', 'the end.'])
        noise = [L('U', 500), L('•*v', 600), L('real words here', 700)]
        self.assertEqual([l['text'] for l in T.body(noise, 2600, set())], ['real words here'])


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
