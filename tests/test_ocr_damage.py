"""tools/ocr_damage.py (Round 8, Job C3 proposal): the four kinds of damage the read gate misses."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import ocr_damage as D  # noqa: E402
import transcribe_scan as T  # noqa: E402


class Damage(unittest.TestCase):
    def test_kinds(self):
        acc, ver = {'café'}, {'Kraków'}
        self.assertEqual(D.kind('Cloriviére:', acc, ver), 'accent-in-word')
        self.assertEqual(D.kind('“IIX\\ovcuos', acc, ver), 'symbol-in-word')
        self.assertEqual(D.kind('1bid.,', acc, ver), 'digit-glued')
        self.assertEqual(D.kind('Church.*°', acc, ver), 'note-mark')
        for fine in ('café', 'Kraków', '1944', '2nd', '8vo', 'the', 'Œuvres'):
            self.assertIsNone(D.kind(fine, acc, ver), fine)

    def test_the_current_gate_misses_them(self):
        V = T.vocabulary()
        for tok in ('Cloriviére', '1bid', 'IIX\\ovcuos', '*°'):
            self.assertNotEqual(T.repair(tok, V)[1], 'unknown', tok)  # why this proposal exists


if __name__ == '__main__':
    unittest.main()
