"""Unlimited-OCR-2 scaffold (tools/ocr/unlimited/): an optional third engine, off by default (round 4, Job 4).

No model runs anywhere: these tests use a stub HTTP server and stored sample output only, and prove that without the flag
and an endpoint tools/transcribe_scan.py behaves exactly as before."""
import http.server, json, sys, tempfile, threading, unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import transcribe_scan as T  # noqa: E402
from ocr.unlimited import client as C, postprocess as P, structure as S  # noqa: E402

RAW = (ROOT / 'tests/fixtures/unlimited_ocr/sample_raw.txt').read_text(encoding='utf-8')


class StubServer(http.server.BaseHTTPRequestHandler):
    """An OpenAI-compatible chat-completions stand-in: replies with one page of stored output per image it receives."""
    requests = []
    stream = True

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        StubServer.requests.append(body)
        n = sum(1 for p in body['messages'][0]['content'] if p['type'] == 'image_url')
        text = ''.join('<PAGE><BLOCK>text[100,100,900,150]<FORK>page text %d' % (len(StubServer.requests) * 10 + i) for i in range(n))
        self.send_response(200)
        self.end_headers()
        if body.get('stream'):
            half = len(text) // 2
            for piece in (text[:half], text[half:]):
                self.wfile.write(b'data: ' + json.dumps({'choices': [{'delta': {'content': piece}}]}).encode() + b'\n\n')
            self.wfile.write(b'data: {"choices": [], "usage": {"completion_tokens": 9}}\n\ndata: [DONE]\n\n')
        else:
            self.wfile.write(json.dumps({'choices': [{'message': {'content': text}}]}).encode())

    def log_message(self, *a):
        pass


class Client(unittest.TestCase):
    def setUp(self):
        StubServer.requests = []
        self.srv = http.server.HTTPServer(('127.0.0.1', 0), StubServer)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.url = 'http://127.0.0.1:%d' % self.srv.server_port
        self.tmp = tempfile.TemporaryDirectory()
        self.imgs = []
        for i in range(3):
            p = Path(self.tmp.name) / f'page_{i + 1:04d}.jpg'
            p.write_bytes(b'\xff\xd8fake')
            self.imgs.append(p)

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()
        self.tmp.cleanup()

    def test_prompt_and_payload_follow_the_official_format(self):
        self.assertEqual(C.build_prompt(3), '<PAGE><image><PAGE><image><PAGE><image>Multi page parsing.')
        with self.assertRaises(ValueError):
            C.build_prompt(0)
        p = C.build_payload(self.imgs[:2], C.UnlimitedOCRConfig(endpoint='x'))
        content = p['messages'][0]['content']
        self.assertEqual([c['type'] for c in content], ['image_url', 'image_url', 'text'])  # images first, then the prompt
        self.assertTrue(content[0]['image_url']['url'].startswith('data:image/jpeg;base64,'))
        self.assertFalse(p['skip_special_tokens'])
        self.assertEqual(p['max_tokens'], 16000)
        self.assertEqual(p['custom_params'], {'ngram_size': 35, 'window_size': 1024, 'page_token_id': 128827, 'eos_token_id': 1,
                                              'max_page_tokens': 20000})
        self.assertEqual(C.build_payload(self.imgs[:1], C.UnlimitedOCRConfig(endpoint='x'))['custom_params']['window_size'], 128)

    def test_streaming_and_plain_responses_through_a_stub_server_in_page_windows(self):
        cl = C.UnlimitedOCRClient(C.UnlimitedOCRConfig(endpoint=self.url, page_window=2))
        raw = cl.raw_for_images(self.imgs)
        self.assertEqual(len(StubServer.requests), 2)  # pages 1-2, then page 3
        self.assertEqual(raw.count('<PAGE>'), 3)  # one per input page, in order
        StubServer.requests = []
        cl = C.UnlimitedOCRClient(C.UnlimitedOCRConfig(endpoint=self.url, page_window=10, stream=False))
        self.assertEqual(cl.raw_for_images(self.imgs).count('<PAGE>'), 3)
        self.assertEqual(len(StubServer.requests), 1)

    def test_pymupdf_is_imported_lazily(self):
        self.assertNotIn('fitz', sys.modules.get('ocr.unlimited.client').__dict__)


class PostProcess(unittest.TestCase):
    def test_raw_blocks_become_page_bounded_markdown(self):
        pages = P.parse(RAW)
        self.assertEqual(len(pages), 4)  # the blank second page keeps its place
        self.assertEqual(pages[1], [])
        md = P.to_markdown(RAW)
        self.assertEqual(md.count('<!-- page '), 4)
        self.assertIn('# THE MYSTERY OF INIQUITY', md)
        self.assertIn('## Chapter 1', md)
        self.assertIn('![](page3_120_520_880_760.jpg)', md)
        self.assertIn('The two viewpoints are completely <!-- continued on next page -->', md)
        self.assertIn('<!-- continued from previous page -->\nand utterly different.', md)  # marked, never merged across pages
        self.assertNotIn('<BLOCK>', md)
        self.assertNotIn('<FORK>', md)

    def test_lines_are_spread_down_the_block_box_in_djvu_coordinates(self):
        lines = P.page_lines(P.parse(RAW)[2], 2000, 3000)
        body = [l for l in lines if l['text'].startswith(('CATHOLICS', 'the ills', 'remedies'))]
        self.assertEqual(len(body), 3)
        self.assertEqual((body[0]['x'], body[0]['x2'], body[0]['top']), (200, 1800, 900))
        self.assertEqual(body[2]['y'], 1500)
        self.assertFalse(any(l['text'] == '' for l in lines))  # the figure gives no line


class Structure(unittest.TestCase):
    def test_title_author_imprint_and_page_ranges(self):
        st = S.structure(RAW)
        self.assertEqual(st['pages'], 4)
        self.assertEqual(st['titleCandidates'][0], {'text': 'THE MYSTERY OF INIQUITY', 'page': 1})
        self.assertEqual(st['authorCandidates'][0]['text'], 'PAUL HANLY FURFEY')
        self.assertTrue(any('BRUCE PUBLISHING' in i['text'] for i in st['imprintLines']))
        self.assertIn({'year': 1944, 'page': 1}, st['yearsSeen'])
        self.assertEqual([h['text'] for h in st['headings']][-1], 'Chapter 2')
        self.assertEqual(st['pageRanges'][-1], {'heading': 'Chapter 2', 'pages': [4, 4]})
        self.assertIn('confirm every value', st['note'])


DJVU = """<?xml version="1.0"?><DjVuXML><BODY>
<OBJECT usemap="scan_0001.djvu" width="2000" height="3000"><HIDDENTEXT><PAGECOLUMN><REGION><PARAGRAPH>
<LINE><WORD coords="200,990,700,900">CATHOLICS</WORD><WORD coords="720,990,900,900">hawe</WORD><WORD coords="920,990,1100,900">their</WORD><WORD coords="1120,990,1300,900">own</WORD></LINE>
<LINE><WORD coords="200,1190,500,1100">the</WORD><WORD coords="520,1190,800,1100">ills</WORD><WORD coords="820,1190,1100,1100">which</WORD></LINE>
<LINE><WORD coords="200,1390,700,1300">remedies.</WORD></LINE>
</PARAGRAPH></REGION></PAGECOLUMN></HIDDENTEXT></OBJECT></BODY></DjVuXML>"""


class FakeClient:
    calls = 0

    def raw_for_images(self, images):
        FakeClient.calls += 1
        return '<PAGE><BLOCK>text[100,300,900,460]<FORK>CATHOLICS have their own\nthe ills which\nremedies.'


class TranscribeScanEngine(unittest.TestCase):
    V = {'catholics': 9, 'have': 99, 'their': 99, 'own': 99, 'the': 99, 'ills': 9, 'which': 99, 'remedies': 9}

    def run_build(self, cache, unlimited=None):
        e = {'edition': 'ia-scan', 'ia': 'scan', 'firstLeaf': 0, 'lastLeaf': 0}
        return T.build(e, cache, self.V, unlimited)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        c = Path(self.tmp.name)
        (c / 'scan_djvu.xml').write_text(DJVU)
        (c / 'scan.meta.json').write_text('{}')
        (c / 'scan.where.json').write_text('{"server": "example.invalid", "dir": "/x"}')
        img = c / 'img' / 'scan'
        img.mkdir(parents=True)
        (img / '0001-s1.jpg').write_bytes(b'\xff\xd8fake')

    def tearDown(self):
        self.tmp.cleanup()

    def test_off_by_default_scores_and_text_unchanged(self):
        with mock.patch.object(T, 'third_ocr', side_effect=AssertionError('third engine must not run')):
            before = self.run_build(self.tmp.name)
        after = self.run_build(self.tmp.name, None)
        self.assertEqual(before[:5], after[:5])  # paragraphs, corrections, flagged, words, unknown
        self.assertNotIn('thirdOcr', before[7])
        self.assertIn('hawe', before[0][0])  # the archive.org reading stands
        rg = T.read_gate_record({'firstLeaf': 0, 'lastLeaf': 0}, before[3], before[4], before[7])
        self.assertNotIn('thirdOcr', rg)
        self.assertEqual(T.choose_lines([], [], self.V), ([], {}))  # the Tesseract path keeps its default engine name

    def test_with_flag_and_endpoint_the_third_engine_is_chosen_per_line(self):
        FakeClient.calls = 0
        with mock.patch('ocr.unlimited.client.UnlimitedOCRClient', return_value=FakeClient()):
            out = self.run_build(self.tmp.name, 'http://127.0.0.1:1')
        self.assertEqual(FakeClient.calls, 1)
        self.assertIn('CATHOLICS have their own', out[0][0])
        self.assertEqual(out[7]['thirdOcr']['lineChoices'], {'unlimited-ocr': 1})
        self.assertTrue((Path(self.tmp.name) / 'uocr' / 'scan' / '0001-s1.txt').exists())  # raw output is cached
        rg = T.read_gate_record({'firstLeaf': 0, 'lastLeaf': 0}, out[3], out[4], out[7])
        self.assertEqual(rg['thirdOcr']['lineChoices'], {'unlimited-ocr': 1})


if __name__ == '__main__':
    unittest.main()
