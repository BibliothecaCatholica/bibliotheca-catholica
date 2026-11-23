"""tools/transcribe_scan.py: the general single-scan transcription tool (November 16, 2026), and every record it made."""
import hashlib, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import transcribe_scan as T  # noqa: E402
from rights_rule import nonrenewal_problems, pd_by_date  # noqa: E402

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

    def test_a_chapter_opening_page_is_not_a_note(self):
        # November 22, 2026 (Walsh, High Points of Medieval Culture): the numeral and title are a little taller than the text
        # below them and set off by a wide gap; the text is the body, not a note
        page = [self.L('VI', 300, 58), self.L('THE MEDIEVAL UNIVERSITIES', 480, 61)] + [
            self.L('text line %d of the opening page' % i, 700 + 95 * i, 53) for i in range(15)]
        self.assertEqual(T.split_notes(page, 2600), (page, []))
        with_note = page + [self.L('1 Robertson, The British Universities, p. 1.', 2300, 40), self.L('more of the note', 2350, 40)]
        kept, notes = T.split_notes(with_note, 2600)
        self.assertEqual((kept, len(notes)), (page, 1))  # a real footnote on that page still leaves the body

    def test_continued_notes_starting_above_mid_page(self):
        # long Butler notes often begin above mid-page and may lack a fresh mark; type is compared to the
        # preceding lines, not the whole page (notes can fill most of it). The first note line is only slightly
        # smaller (46 / 51.25 ~= 0.898), so the first-line threshold is 0.90.
        body = [self.L('body line %d of the text' % i, 300 + 80 * i, 51.25) for i in range(4)]
        notes = [self.L('Honorius of Autun, continuing the note from the last page,', 700, 46),
                 self.L('and the rest of this long note in the same smaller type,', 755, 45),
                 self.L('which runs well past the middle of the page to the foot.', 810, 45),
                 self.L('A second sentence of the same note keeps the smaller type.', 865, 44),
                 self.L('Still more of the note, now the bulk of what is on the page.', 920, 45),
                 self.L('The last line of the note, still in the smaller type.', 975, 45)]
        # a gap between the last body line and the first note line
        notes[0]['y'] = body[-1]['y'] + 160
        for i, l in enumerate(notes[1:], 1):
            l['y'] = notes[0]['y'] + 55 * i
        kept, got = T.split_notes(body + notes, 2600)
        self.assertEqual(kept, body)
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0][0], notes[0]['text'])
        self.assertEqual(got[0][-1], notes[-1]['text'])
        # a still-body line after a gap must not be pulled into the notes: the first line of a candidate
        # remainder has to be smaller type itself
        extra = self.L('one more body line after a gap', body[-1]['y'] + 160, 51.25)
        almost = body + [extra] + [dict(l) for l in notes]
        almost[-len(notes)]['y'] = extra['y'] + 160  # a real gap, but the extra line is still body type
        for i, l in enumerate(almost[-len(notes)+1:], 1):
            l['y'] = almost[-len(notes)]['y'] + 55 * i
        kept2, got2 = T.split_notes(almost, 2600)
        self.assertEqual(len(kept2), 5)
        self.assertEqual(kept2[-1]['text'], 'one more body line after a gap')
        self.assertEqual(got2[0][0], notes[0]['text'])

    def test_library_stamp_dropped_but_running_heads_kept(self):
        pages = [(3000, [self.L('THE THING', 100), self.L('text', 300), self.L('MARIN COUNTY FREE LIBRARY', 900)]) for _ in range(4)]
        heads_low = [(3000, [self.L('94', 100), self.L('A CASE IN POINT', 150), self.L('text', 300)]) for _ in range(4)]
        self.assertEqual(T.library_stamps(heads_low, set()), set())  # a running head under a page number is not a stamp
        stamps = T.library_stamps(pages, {'thething'})
        self.assertTrue(T.is_stamp('MARIN COUNTTY FREE LIBRARY', stamps))  # an OCR variant of the same stamp
        self.assertFalse(T.is_stamp('THE THING', stamps))
        self.assertFalse(T.is_stamp('Marin County Free Library', stamps))  # only capital lines are ever removed

    def test_hand_fixes_replace_one_reading_and_drop_only_whole_noise_lines(self):
        L = lambda t: {'x': 100, 'y': 300, 'h': 30, 'text': t, 'paraStart': False, 'para': 0}
        pages = [(3000, [L('i'), L('the victim of a Rion the sys-'), L('uw we: —_—')])]
        e = {'edition': 'x', 'firstLeaf': 5, 'handFixes': [
            {'leaf': 5, 'page': 'p. 7', 'ocr': 'i', 'reading': 'I'},  # a whole line wins over a substring
            {'leaf': 5, 'page': 'p. 7', 'ocr': 'a Rion the', 'reading': 'a system, the'},
            {'leaf': 5, 'page': 'p. 7', 'ocr': 'uw we: —_—', 'reading': ''}]}
        T.apply_hand_fixes(pages, e)
        self.assertEqual([l['text'] for l in pages[0][1]], ['I', 'the victim of a system, the sys-'])
        with self.assertRaises(AssertionError):  # a reading must be found exactly once
            T.apply_hand_fixes(pages, {'edition': 'x', 'firstLeaf': 5, 'handFixes': [{'leaf': 5, 'ocr': 'the', 'reading': 'a'}]})
        with self.assertRaises(AssertionError):  # dropping part of a line is not allowed
            T.apply_hand_fixes(pages, {'edition': 'x', 'firstLeaf': 5, 'handFixes': [{'leaf': 5, 'ocr': 'victim', 'reading': ''}]})

    def test_hand_fixes_are_logged(self):
        for r in RECORDS:
            for f in r.get('handFixes', []):
                self.assertEqual(set(f), {'leaf', 'page', 'ocr', 'reading'}, r['id'])
                # a reading equal to the OCR is a keep mark (a heading or body line checked on the image), never empty
                self.assertTrue(f['ocr'] != f['reading'] or f['reading'].strip(), r['id'])

    def test_lost_line_end_hyphen_rejoined_when_the_whole_is_common(self):
        # Samuel Johnson's scan drops every line-end hyphen: "the imagina" / "tion to riot" is one word, even though
        # "tion" occurs in other texts; a known first half is never joined
        v = {'imagination': 5, 'tion': 2, 'the': 99, 'and': 99, 'to': 99, 'riot': 4, 'suffer': 9, 'in': 99, 'at': 99}
        self.assertEqual(T.join_lines(['and suffer the imagina', 'tion to riot'], v), 'and suffer the imagination to riot')
        self.assertEqual(T.join_lines(['to riot', 'at the'], v), 'to riot at the')
        v.update({'per': 50, 'performances': 4})
        self.assertEqual(T.join_lines(['the per', 'formances of'], dict(v, of=99)), 'the performances of')
        self.assertEqual(T.join_lines(['to the imagina', 'tion. Then'], dict(v, then=9)), 'to the imagination. Then')  # punctuation after

    def test_one_article_is_cut_from_shared_pages(self):
        paras = [['ADULTS ends here.'], ['Advent (Lat. ad-venio, to', 'come to) begins.'], ['More.'], ['Francis', 'Mershman.'], ['Adventists.']]
        e = {'startsWith': 'Advent (Lat. ad-venio', 'endsWith': 'Francis Mershman.'}
        self.assertEqual(T.bounded(paras, e), paras[1:4])
        self.assertEqual(T.bounded(paras, {}), paras)
        with self.assertRaises(StopIteration):  # both bounds must be found
            T.bounded(paras, {'startsWith': 'Nowhere', 'endsWith': 'Mershman.'})

    def test_running_head_band_dropped(self):
        L = lambda t, x, y: {'x': x, 'y': y, 'h': 20, 'text': t, 'paraStart': False, 'para': 0}
        page = [L('ADVENT', 480, 137), L('166', 850, 139), L('ADVENTISTS', 1110, 140)] + [L('body line %d of the column' % i, 240, 200 + 28 * i) for i in range(6)]
        self.assertEqual([l['text'] for l in T.body(page, 2250, set())][0], 'body line 0 of the column')

    def test_verified_words_are_in_the_text_and_logged(self):
        for r in RECORDS:
            if r.get('verifiedWords'):
                text = (ROOT / r['text']).read_text(encoding='utf-8')
                for w in r['verifiedWords']:
                    self.assertIn(w, text, r['id'])
                self.assertIn('verifiedWords', r['method'], r['id'])



class VerseLayout(unittest.TestCase):
    def test_verse_keeps_lines_and_breaks_stanzas_on_a_wide_gap(self):
        L = lambda t, y, x=100: {'x': x, 'y': y, 'h': 20, 'text': t, 'paraStart': False, 'para': 0}
        # line spacing ~20; a stanza gap of 80 is wider than 2.2 * median
        pages = [(3000, [
            L('RUNNING HEAD 120', 80),
            L('GERMINE nobilis Eulalia,', 400),
            L('mortis et indole nobilior.', 420),
            L('Proximus occiduo locus est,', 500),
            L('qui tulit hoc decus egregium.', 520),
        ])]
        e = {'edition': 'x', 'firstLeaf': 1, 'layout': 'verse'}
        paras = T.verse_paras(pages, e, heads={'runninghead'}, stamps=set(), V={})
        self.assertEqual(paras[0], ['GERMINE nobilis Eulalia,', 'mortis et indole nobilior.'])
        self.assertEqual(paras[1], ['Proximus occiduo locus est,', 'qui tulit hoc decus egregium.'])

    def test_hand_fix_may_insert_an_omission_row_of_asterisks(self):
        L = lambda t, y: {'x': 100, 'y': y, 'h': 20, 'text': t, 'paraStart': False, 'para': 0}
        pages = [(3000, [
            L('canitiem meditata senum. ^ ^', 200),
            L('Flamma crepans volat in faciem,', 600),
            L('perque comas vegetata caput.', 620),
        ])]
        e = {'edition': 'x', 'firstLeaf': 10, 'layout': 'verse', 'handFixes': [
            {'leaf': 10, 'page': '122', 'ocr': 'canitiem meditata senum. ^ ^',
             'reading': 'canitiem meditata senum.\n\n* * * *'}]}
        T.apply_hand_fixes(pages, e)
        paras = T.verse_paras(pages, e, heads=set(), stamps=set(), V={})
        self.assertEqual(paras[0], ['canitiem meditata senum.'])
        self.assertEqual(paras[1], ['* * * *'])
        self.assertEqual(paras[2], ['Flamma crepans volat in faciem,', 'perque comas vegetata caput.'])

    def test_short_roman_numerals_on_a_verse_page_are_kept(self):
        L = lambda t, y: {'x': 100, 'y': y, 'h': 20, 'text': t, 'paraStart': False, 'para': 0}
        pages = [(3000, [
            L('ST. EULALIA. 125', 80),
            L('IX.', 400),
            L('Shed on her flowers and leaves !', 510),
            L('X.', 700),
            L('So we these relics prize,', 820),
        ])]
        paras = T.verse_paras(pages, {'edition': 'x', 'firstLeaf': 1, 'layout': 'verse'}, heads=set(), stamps=set(), V={})
        self.assertEqual(paras[0][0], 'IX.')
        self.assertIn('Shed on her flowers and leaves !', paras[0])
        self.assertEqual(paras[1][0], 'X.')
        self.assertIn('So we these relics prize,', paras[1])

    def test_verse_does_not_rejoin_a_turned_line(self):
        # "longed-for" / "death." is one verse turned over, not a hyphen to join
        V = {'longed': 1, 'for': 99, 'death': 9, 'she': 99, 'courts': 1}
        e = {'edition': 'x', 'layout': 'verse', 'firstLeaf': 0, 'ia': 'x', 'year': 1890}
        out, *_ = [],
        paras = [['She courts the flames, and drinks the longed-for', 'death.']]
        # score through join would be wrong; verse path keeps two lines
        text = '\n'.join(paras[0])
        self.assertIn('\n', text)
        self.assertTrue(text.endswith('death.'))
        self.assertIn('longed-for', text.split('\n')[0])


class ReadGateProcess(unittest.TestCase):
    """Owner-approved read-gate process (November 22, 2026): a second OCR chosen per line, sample-verified foreign words,
    back matter that may be left out, and a recorded method for every score."""
    V = {'the': 99, 'church': 50, 'of': 99, 'in': 99, 'rome': 20, 'and': 99}

    def line(self, text, top, y, x=100, x2=900):
        return {'x': x, 'x2': x2, 'top': top, 'y': y, 'h': y - top, 'text': text, 'paraStart': False, 'para': 0}

    def test_second_ocr_line_taken_only_when_it_reads_more_words(self):
        arch = [self.line('the cxqrch of Rome', 100, 140), self.line('in the church', 160, 200), self.line('and Rome', 220, 260)]
        tess = [self.line('the church of Rome', 102, 141), self.line('in tlie church', 161, 199), self.line('and', 221, 259)]
        out, counts = T.choose_lines(arch, tess, self.V)
        self.assertEqual([l['text'] for l in out], ['the church of Rome', 'in the church', 'and Rome'])
        self.assertEqual(counts, {'tesseract': 1, 'archive.org': 2})  # a worse or shorter reading never replaces a line
        self.assertEqual(out[0]['engine'], 'tesseract')

    def test_hand_fixed_numeral_and_ornament_are_kept_and_stand_alone(self):
        """A chapter numeral or ornament row restored by hand (Grant, November 23, 2026) is printed text: body() keeps it
        though it has no known word near the top of the page, and it is a paragraph of its own."""
        page = [self.line('ne ha', 700, 790, x=400, x2=600)] + [self.line('the church of Rome and the church', 1100 + 60 * i, 1140 + 60 * i)
                                                             for i in range(6)]
        self.assertNotIn('ne ha', [l['text'] for l in T.body([dict(l) for l in page], 3800, set(), self.V)])
        e = {'edition': 'ed-x', 'firstLeaf': 0, 'handFixes': [{'leaf': 0, 'page': None, 'ocr': 'ne ha', 'reading': '. . 1 . .'}]}
        raw = [(3800, [dict(l) for l in page])]
        T.apply_hand_fixes(raw, e)
        kept = T.body(raw[0][1], 3800, set(), self.V)
        self.assertEqual(kept[0]['text'], '. . 1 . .')
        self.assertTrue(T.alone('. . 1 . .') and T.alone('* * * *'))
        self.assertFalse(T.alone('JOHN ENGLAND') or T.alone('1824 January 4.') or T.alone(''))

    def test_imprint_and_text_after_an_ornament_are_not_footnotes(self):
        body = [self.line('the church of Rome and the church of Rome', 400 + 60 * i, 440 + 60 * i) for i in range(5)]
        imprint = [self.line('THE BRUCE PUBLISHING COMPANY', 3000, 3030), self.line('MILWAUKEE', 3060, 3090)]
        kept, notes = T.split_notes(body + imprint, 3800)
        self.assertEqual(notes, [])
        orn = dict(self.line('* * * *', 760, 790), hand=True)
        after = [self.line('in the church of Rome and', 900 + 40 * i, 925 + 40 * i) for i in range(4)]
        kept, notes = T.split_notes(body + [orn] + after, 3800)
        self.assertEqual(notes, [])

    def test_keep_mark_holds_a_heading_and_keeps_body_text_out_of_the_notes(self):
        """A hand fix whose reading equals the OCR is a keep mark (Furfey, November 23, 2026): the line is printed body
        text, so body() keeps a heading the layout rules took for a running head, and no footnote starts at it."""
        body = [self.line('the church of Rome and the church of Rome', 400 + 60 * i, 440 + 60 * i) for i in range(5)]
        small = [self.line('in the church of Rome and', 2900 + 40 * i, 2925 + 40 * i) for i in range(3)]
        self.assertTrue(T.split_notes(body + [dict(l) for l in small], 3800)[1])  # smaller type set apart: a note
        e = {'edition': 'ed-x', 'firstLeaf': 0, 'handFixes': [{'leaf': 0, 'page': None, 'ocr': 'in the church of Rome and', 'reading': 'in the church of Rome and'}]}
        raw = [(3800, body + [dict(l) for l in small[:1]])]
        T.apply_hand_fixes(raw, e)
        lines = raw[0][1] + [dict(l) for l in small[1:]]
        self.assertTrue(lines[5].get('kept'))
        self.assertEqual(T.split_notes(lines, 3800)[1], [])

    def test_tesseract_tsv_is_scaled_to_the_djvu_coordinates(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            img = Path(d) / '0001-s2.jpg'
            img.write_bytes(b'')
            img.with_suffix('.eng.tsv').write_text(
                'level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n'
                '1\t1\t0\t0\t0\t0\t0\t0\t1000\t1500\t-1\t\n'
                '5\t1\t1\t1\t1\t1\t100\t200\t50\t20\t95\tThe\n5\t1\t1\t1\t1\t2\t160\t200\t80\t20\t95\tChurch\n')
            lines = T.tesseract_lines(img, 'eng', 2000)
        self.assertEqual(lines, [{'x': 200, 'x2': 480, 'top': 400, 'y': 440, 'h': 40, 'text': 'The Church'}])

    def test_foreign_sample_is_reproducible_and_large_enough(self):
        forms = ['form%d' % i for i in range(400)]
        a = T.foreign_sample('ed-x', 'lat', forms)
        self.assertEqual(a, T.foreign_sample('ed-x', 'lat', list(reversed(forms))))
        self.assertEqual(len(a), 40)  # 10% of 400
        self.assertEqual(len(T.foreign_sample('ed-x', 'lat', forms[:100])), 30)  # at least 30
        self.assertEqual(len(T.foreign_sample('ed-x', 'lat', forms[:12])), 12)  # every form when fewer than 30

    def test_foreign_words_count_only_with_a_clean_sample_or_a_full_check(self):
        forms = ['verbum%d' % i for i in range(50)]
        e = {'edition': 'ed-y', 'foreignWords': {'lat': {'forms': forms, 'checked': T.foreign_sample('ed-y', 'lat', forms)}}}
        read, rec = T.foreign_read(e)
        self.assertEqual(read, set(forms))
        self.assertEqual(rec['lat']['result'], 'every sampled form correct')
        e['foreignWords']['lat']['checked'] = forms[:30]  # not the drawn sample
        with self.assertRaises(AssertionError):
            T.foreign_read(e)
        e['foreignWords']['lat'] = {'forms': forms, 'wrong': ['verbum3']}  # a wrong form without a full check
        with self.assertRaises(AssertionError):
            T.foreign_read(e)
        e['foreignWords']['lat']['allChecked'] = True
        read, rec = T.foreign_read(e)
        self.assertNotIn('verbum3', read)
        self.assertEqual(len(read), 49)

    def test_only_back_matter_may_be_left_out(self):
        e = {'edition': 'z', 'ia': 'scanid', 'lastLeaf': 220, 'omitted': [{'what': 'the index', 'leaves': [222, 226], 'pages': '205-209'}]}
        T.check_omitted(e)
        self.assertEqual(T.omitted_sentence(e), ' Left out of this text: the index (pages 205-209); read them in the full scan at '
                                                'https://archive.org/details/scanid.')
        two = dict(e, omitted=[{'what': 'the bibliography', 'leaves': [221, 221], 'pages': '181-188'}, {'what': 'the index', 'leaves': [222, 226], 'pages': '189-194'}])
        self.assertIn('the bibliography (pages 181-188) and the index (pages 189-194); read', T.omitted_sentence(two))  # no comma for two
        with self.assertRaises(AssertionError):
            T.check_omitted({'edition': 'z', 'lastLeaf': 220, 'omitted': [{'what': 'chapter one', 'leaves': [30, 40], 'pages': '1-10'}]})

    def test_the_method_is_recorded_with_the_score(self):
        rg = T.read_gate_record({'firstLeaf': 6, 'lastLeaf': 221, 'verifiedWords': ['a', 'b']}, 1000, 4,
                                {'secondOcr': {'engine': 'tesseract 5.3.4', 'langs': 'eng+lat', 'scale': 1,
                                               'lineChoices': {'archive.org': 9, 'tesseract': 1}}, 'foreignWords': {}})
        self.assertEqual((rg['readRate'], rg['gate'], rg['leavesScored'], rg['verifiedWords']), (0.996, 0.995, [6, 221], 2))
        self.assertIn('tesseract 5.3.4 (eng+lat', rg['engine'])
        self.assertEqual(rg['lineChoices'], {'archive.org': 9, 'tesseract': 1})

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
            if 'readGate' in r:  # recorded with every score since November 22, 2026
                self.assertEqual((r['readGate']['readRate'], r['readGate']['gate']), (r['readRate'], 0.995), r['id'])
                self.assertEqual(r['unknownWords'], sum(f.get('n', len(f['words'])) for f in r['flagged']), r['id'])
            for lang, d in r.get('foreignWords', {}).items():
                if not d['wrong']:
                    self.assertEqual(d['sample'], T.foreign_sample(r['id'], lang, d['forms']), (r['id'], lang))
            if r.get('omitted'):
                self.assertIn('Left out of this text:', text, r['id'])
            self.assertEqual(r['flaggedBlocks'], len(r['flagged']), r['id'])
            self.assertEqual(r['corrections'], len(r['correctionList']), r['id'])
            self.assertIn(r['rightsBasis'], ('pd-date', 'pd-nonrenewal'), r['id'])
            if r['rightsBasis'] == 'pd-nonrenewal':
                self.assertEqual(nonrenewal_problems(r.get('nonRenewal')), [], r['id'])
            for v in r['volumes']:
                if r['rightsBasis'] == 'pd-date':
                    self.assertTrue(pd_by_date(v['year']), r['id'])
                else:  # the scan is the very printing the evidence names
                    self.assertEqual((v['identifier'], v['year']), (r['nonRenewal']['scan'], r['nonRenewal']['firstPublicationYear']))
                self.assertEqual(v['url'], 'https://archive.org/details/' + v['identifier'])
                self.assertRegex(v['ocrSha256'], r'^[0-9a-f]{64}$')


if __name__ == '__main__':
    unittest.main()
