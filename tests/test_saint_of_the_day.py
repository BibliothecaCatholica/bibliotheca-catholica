"""Saint-of-the-day JSON: 366 days, 2026 scripture citations only, USCCB source, no saints-days edits."""
from __future__ import annotations
import json, re, unittest, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOTD = ROOT / 'data' / 'saint-of-the-day.json'
REFS = ROOT / 'data' / 'lectionary-references-2026.json'
SAINTS = ROOT / 'data' / 'saints-days.json'
USCCB_PDF = 'https://www.usccb.org/resources/2026cal.pdf'
PROSE = (
    'After the man, Adam',
    'The angel Gabriel was sent',
    'In the beginning was the Word',
    'And the Word became flesh',
)


class SaintOfTheDayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(SOTD.read_text(encoding='utf-8'))
        cls.days = cls.data['days']
        cls.saints = json.loads(SAINTS.read_text(encoding='utf-8'))

    def test_366_days_including_february_29(self):
        self.assertEqual(len(self.days), 366)
        self.assertIn('02-29', self.days)
        self.assertEqual(set(self.days), set(self.saints['days']))

    def test_2026_citations_for_every_civil_day(self):
        with_citations = [k for k, v in self.days.items() if v['readings'].get('citations')]
        self.assertEqual(len(with_citations), 365)
        leap = self.days['02-29']['readings']
        self.assertEqual(leap['year'], None)
        self.assertEqual(leap['citations'], [])
        self.assertIn('29 February is not in 2026', leap['note'])

    def test_citations_only_no_lectionary_text(self):
        blob = json.dumps(self.data)
        for phrase in PROSE:
            self.assertNotIn(phrase, blob)
        for md, day in self.days.items():
            for cite in day['readings'].get('citations') or []:
                self.assertNotIn('—', cite, md)
                self.assertNotIn('\u2014', cite, md)
                self.assertLess(len(cite), 600, md + ': citation looks like prose')

    def test_source_attribution(self):
        src = self.data['readingsSource']
        self.assertEqual(src['url'], USCCB_PDF)
        self.assertIn('United States Conference of Catholic Bishops', src['publisher'])
        self.assertIn('Scripture citations only', src['note'])
        self.assertIn(USCCB_PDF, json.dumps(json.loads(REFS.read_text(encoding='utf-8'))['source']))
        self.assertEqual(self.data['usccbDaily'], 'https://bible.usccb.org/daily-bible-reading')

    def test_january_1_is_mary_mother_of_god(self):
        p = self.days['01-01']['principal']
        self.assertEqual(p['name'], 'Solemnity of Mary, the Holy Mother of God')
        self.assertEqual(p['rank'], 'solemnity')
        self.assertIn('Circumcision', p['note'])
        self.assertIn('left unchanged', p['note'])
        names = [o['name'] for o in self.days['01-01']['observances']]
        self.assertFalse(any('Circumcision' in n for n in names))
        cites = ' '.join(self.days['01-01']['readings']['citations'])
        self.assertIn('Nm 6:22-27', cites)
        self.assertIn('Lk 2:16-21', cites)

    def test_spot_checks(self):
        def name(md):
            return self.days[md]['principal']['name']

        def names(md):
            return [o['name'] for o in self.days[md]['observances']]

        self.assertIn('Francis Xavier', name('12-03'))
        self.assertEqual(self.days['12-03']['principal']['rank'], 'memorial')
        self.assertIn('Nicholas', ' '.join(names('12-06')))
        self.assertIn('Sunday of Advent', name('12-06'))
        self.assertIn('Ambrose', name('12-07'))
        self.assertIn('Immaculate Conception', name('12-08'))
        self.assertEqual(self.days['12-08']['principal']['rank'], 'solemnity')
        self.assertIn('Juan Diego', name('12-09'))
        self.assertIn('Nativity of the Lord', name('12-25'))
        self.assertIn('Stephen', name('12-26'))
        self.assertIn('Holy Family', name('12-27'))
        self.assertIn('John the Apostle', ' '.join(names('12-27')))
        self.assertIn('Holy Innocents', name('12-28'))
        self.assertIn('Thomas Becket', ' '.join(self.days['12-29'].get('optionalMemorials') or []))
        self.assertTrue(any('Becket' in n for n in names('12-29')))
        self.assertIn('Basil the Great', name('01-02'))
        self.assertIn('Gregory Nazianzen', name('01-02'))
        self.assertIn('Presentation of the Blessed Virgin Mary', name('11-21'))
        christmas = self.days['12-25']['readings']['citations']
        self.assertTrue(any(c.startswith('Vigil:') for c in christmas))
        self.assertTrue(any(c.startswith('Day:') for c in christmas))
        souls = ' '.join(self.days['11-02']['readings']['citations'])
        self.assertIn('Any readings', souls)
        self.assertEqual(self.days['12-25']['readings']['usccb'], 'https://bible.usccb.org/bible/readings/122526.cfm')

    def test_pss_prop_stripped_from_feast_names(self):
        for md in ('03-19', '04-02'):
            name = self.days[md]['principal']['name']
            self.assertNotIn('Pss Prop', name, md)
            self.assertNotRegex(name, r'\bPss\b')
        self.assertIn('Joseph', self.days['03-19']['principal']['name'])
        self.assertIn('Holy Thursday', self.days['04-02']['principal']['name'])

    def test_observances_are_names_only(self):
        for md, day in self.days.items():
            for o in day['observances']:
                self.assertNotIn('facts', o, md)
                self.assertIn('name', o)

    def test_builder_does_not_edit_saints_days(self):
        before = SAINTS.read_bytes()
        subprocess.check_call(['python3', str(ROOT / 'tools' / 'build_saint_of_the_day.py')], cwd=ROOT)
        self.assertEqual(before, SAINTS.read_bytes())
        rebuilt = json.loads(SOTD.read_text(encoding='utf-8'))
        self.assertEqual(len(rebuilt['days']), 366)

    def test_build_hook(self):
        pkg = (ROOT / 'package.json').read_text(encoding='utf-8')
        self.assertIn('python3 tools/build_saints.py && python3 tools/build_saint_of_the_day.py &&', pkg)


class MagisteriumDisclosureConfigTests(unittest.TestCase):
    def test_short_form_in_affiliates(self):
        aff = (ROOT / 'data' / 'affiliates.js').read_text(encoding='utf-8')
        self.assertIn("line: 'Affiliate links: we may earn a commission.'", aff)
        self.assertIn("disclosure: 'Affiliate disclosure: Some links are affiliate links.", aff)
        self.assertIn("magisterium: { name: 'Magisterium AI', url: 'https://www.magisterium.com/pro/micah'", aff)
        # partner() in study_partner.py requires name and url to come first
        self.assertRegex(aff, r"magisterium:\s*\{\s*name:\s*'Magisterium AI',\s*url:\s*'https://www\.magisterium\.com/pro/micah'")
        self.assertNotIn('short:', aff)

    def test_disclosure_copy_has_research_long_form(self):
        import sys
        sys.path.insert(0, str(ROOT / 'tools'))
        import site_copy
        html = site_copy.disclosure_page('Some links are affiliate links. If you buy through them, Bibliotheca Catholica may earn a small commission at no extra cost to you. It helps keep the library free.')
        self.assertIn('participant in the Magisterium AI affiliate program', html)
        self.assertIn('https://www.magisterium.com/pro/micah', html)
        self.assertIn('Readers who subscribe to Magisterium AI through our links currently receive 25% off, and Bibliotheca Catholica earns a commission (currently 10%) on those subscriptions, at no extra cost to you. Magisterium AI does not endorse or control Bibliotheca Catholica.', html)
        self.assertNotIn('up to 25%', html)
        self.assertIn('not a donation to the library', html)
        self.assertIn('should be checked against the sources they cite', html)
        self.assertIn('href="/about/magisterium-ai/"', html)
        self.assertNotIn('—', html)
        self.assertNotIn('tax-deductible', html.lower())


if __name__ == '__main__':
    unittest.main()
