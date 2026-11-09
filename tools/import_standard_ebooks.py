"""Import a Standard Ebooks edition as a hosted reading-room text (one-off, network; not part of `npm run build`).

First use (2026-11-09): The Incredulity of Father Brown (G. K. Chesterton, 1926). Project Gutenberg has no US
ebook of it. Standard Ebooks dedicates its contributions to the public domain (CC0 1.0); its text is based on the
Faded Page transcription (Distributed Proofreaders Canada, 2012, from the 1947 Cassell omnibus) and on the Internet
Archive scan of the Cassell 1926 printing (in.ernet.dli.2015.463891). Our corrections below restore the 1926 wording.

Usage:
    python3 tools/import_standard_ebooks.py incredulity-father-brown

It downloads the source XHTML files at the pinned commit from GitHub (raw.githubusercontent.com), converts them
to plain text (one paragraph per block, verse lines kept, italics and abbreviation markup dropped, U+2060 word
joiners removed, <hr/> scene breaks as "* * *"), writes data/texts/<edition>.txt, and writes
data/sources/<edition>.json with the SHA-256 of every source file, of their concatenation (sourceFileSha256),
and of the hosted text. It never edits data/library.json: copy the printed sha256 there and run `npm run build`.
"""
import hashlib, html, json, re, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = {'User-Agent': 'BibliothecaCatholica-catalog/1.0 (+https://bibliothecacatholica.com)'}

BOOKS = {
 'incredulity-father-brown': dict(
  edition='se-incredulity-father-brown',
  repo='standardebooks/g-k-chesterton_the-incredulity-of-father-brown',
  commit='2bbf5020638f5bc0ab765f5f5ba706d28d66142c',
  page='https://standardebooks.org/ebooks/g-k-chesterton/the-incredulity-of-father-brown',
  title='THE INCREDULITY OF FATHER BROWN',
  source_title='The Incredulity of Father Brown',
  # spine order of the stories (content.opf at the pinned commit), with the heading block written for each
  stories=[
   ('the-resurrection-of-father-brown', 'I. THE RESURRECTION OF FATHER BROWN'),
   ('the-arrow-of-heaven', 'II. THE ARROW OF HEAVEN'),
   ('the-oracle-of-the-dog', 'III. THE ORACLE OF THE DOG'),
   ('the-miracle-of-moon-crescent', 'IV. THE MIRACLE OF MOON CRESCENT'),
   ('the-curse-of-the-golden-cross', 'V. THE CURSE OF THE GOLDEN CROSS'),
   ('the-dagger-with-wings', 'VI. THE DAGGER WITH WINGS'),
   ('the-doom-of-the-darnaways', 'VII. THE DOOM OF THE DARNAWAYS'),
   ('the-ghost-of-gideon-wise', 'VIII. THE GHOST OF GIDEON WISE'),
  ],
  # Word-level corrections to the 1926 text (Bibliotheca Catholica, 2026-11-09). Each is a place where the
  # Standard Ebooks text (which follows the Faded Page transcription of the 1947 Cassell omnibus) differs from
  # BOTH 1926 printings: the Cassell London second impression (August 1926, in.ernet.dli.2015.463891) and the
  # Dodd, Mead New York printing (incredulityoffat0000ches), checked in their Internet Archive OCR and agreeing
  # with each other. Standard Ebooks' spelling and hyphenation modernizations (summerhouse, connection, today,
  # poniard, and so on) are kept. Each old string must occur exactly once.
  corrections=[
   ("reproducing any real ones.", "reproducing any real one."),
   ("pink spots; that it, it was Spanish", "pink spots; that is, it was Spanish"),
   ("Red Indians sitting on the veranda", "Red Indians sitting in the veranda"),
   ("it was the longer and lower sank", "it was the lower and lower sank"),
   ("turned away from his effort, he tottered", "turned away from this effort, he tottered"),
   ("I think I began to see.”", "I think I begin to see.”"),
   ("on him out the sky.", "on him out of the sky."),
   ("was only in this case that a", "was only in his case that a"),
   ("I believe, and Brandon Merton must have", "I believe, and Brander Merton must have"),
   ("white man standing on the top", "white man standing at my side on the top"),
   ("with something like jerk:", "with something like a jerk:"),
   ("the present.”\n\nAnd then saluting the other", "the present.”\n\nAnd saluting the other"),
   ("inference except that his murderer threw an", "inference except that this murderer threw an"),
   ("to be a respector of persons.", "to be a respecter of persons."),
   ("hedge my guide stopped and disentangled", "hedge my guide stooped and disentangled"),
   ("a murderer never gets rid of a", "a murderer never got rid of a"),
   ("closely interlaced but separate boughs", "closely interlaced but still separate boughs"),
   ("I may say I am his secretary", "I may say I’m his secretary"),
   ("Because I have a serious, I might say solemn, reason,”", "Because I have serious, I might say solemn, reasons,”"),
   ("Good Lord, you don’t tell me you think", "Good Lord, don’t tell me you think"),
   ("take much stock of the laws of", "take much stock in the laws of"),
   ("window, which looked out from a wall", "window, which looked from a wall"),
   ("the body. A long garden tub was", "the body. A large garden tub was"),
   ("wouldn’t it be as well if you had", "wouldn’t it be well if you had"),
   ("He paused again, tracing plans like", "He paused again, still tracing plans like"),
   ("mere drawing scratched upon the stone", "mere drawing scratched or scrawled upon the stone"),
   ("the last that death would strike", "the last that my death would strike"),
   ("which the great sea itself ran", "which the great grey sea itself ran"),
   ("see why you should have done him", "see why you shouldn’t have done him"),
   ("say made up more casually and", "say made up much more casually and"),
   ("a crack, doubtless accidently left ajar", "a crack, doubtless accidentally left ajar"),
   ("It was by that that Arnold Aylmer", "It was by this that Arnold Aylmer"),
   ("am morally certain you wo", "am mortally certain you wo"),
   ("I think that unconsciousness of mine will", "I think that inconsciousness of mine will"),
   ("melodrama: the heir back from the", "melodrama: the heir coming back from the"),
   ("what sort of man was the", "what sort of a man was the"),
   ("also doesn’t exist. Now, do", "also didn’t exist. Now, do"),
   ("you will excuse me putting it before", "you will excuse my putting it before"),
   ("chambers was that both violated the", "chambers was that they both violated the"),
   ("end of the county. In all three", "end of the country. In all three"),
   ("it’s God truth as well", "it’s God’s truth as well"),
   ("“Why he curses priests from morning", "“Why he cursed priests from morning"),
   ("“He curses priests for failing", "“He cursed priests for failing"),
   ("repeated Byme, mystified.", "repeated Byrne, mystified."),
   ("have the three millionaires in that", "have the three great millionaires in that"),
   ("rivals who were ruining him for standing", "rivals who were running him for standing"),
  ],
  header=[
   'THE INCREDULITY OF FATHER BROWN',
   'By G. K. Chesterton',
   'First published 1926 (London: Cassell and Company; New York: Dodd, Mead and Company). Public domain in the USA.',
   'Source: the Standard Ebooks edition (https://standardebooks.org/ebooks/g-k-chesterton/the-incredulity-of-father-brown), whose contributors dedicate their work to the public domain under CC0 1.0. Standard Ebooks based it on the Faded Page transcription by Barbara Watson, Mary Meehan, Mark Akrigg, and Distributed Proofreaders Canada (2012, from the 1947 Cassell omnibus The Father Brown Stories) and on the Internet Archive scan of the Cassell 1926 printing (in.ernet.dli.2015.463891). Standard Ebooks modernized some spelling and hyphenation. Converted to plain text by Bibliotheca Catholica from the source files at commit 2bbf5020638f5bc0ab765f5f5ba706d28d66142c, with 46 word-level corrections to the reading of both 1926 printings (Cassell, London, and Dodd, Mead, New York), listed in the provenance record.',
  ]),
}


def get(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except Exception:
            if attempt == 3:
                raise
            time.sleep(3)


def clean(s):
    s = re.sub(r'<br\s*/>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s).replace('\u2060', '')
    lines = [re.sub(r'[ \t\r\n]+', ' ', x).strip() for x in s.split('\n')]
    return '\n'.join(x for x in lines if x)


def blocks(xhtml):
    body = xhtml[xhtml.index('<body'):xhtml.index('</body>')]
    body = re.sub(r'<h2[^>]*>.*?</h2>', '', body, flags=re.S)
    out = []
    for m in re.finditer(r'<p[^>]*>(.*?)</p>|<hr\s*/>', body, re.S):
        out.append('* * *' if m.group(0).startswith('<hr') else clean(m.group(1)))
    return [b for b in out if b]


def main(work):
    cfg = BOOKS[work]
    raw = lambda f: get(f"https://raw.githubusercontent.com/{cfg['repo']}/{cfg['commit']}/src/epub/text/{f}.xhtml")
    files, parts = [], []
    for name in ['dedication', 'preface'] + [s for s, _ in cfg['stories']]:
        data = raw(name)
        files.append(dict(file=f'src/epub/text/{name}.xhtml', sha256=hashlib.sha256(data).hexdigest(), bytes=len(data)))
        parts.append((name, data))
    concat = hashlib.sha256(b''.join(d for _, d in parts)).hexdigest()
    doc = {n: d.decode('utf-8') for n, d in parts}
    text = list(cfg['header'])
    text.append(f"*** START OF THE HOSTED TEXT: {cfg['title']} ***")
    ded = blocks(doc['dedication'])
    assert ded == ['To\nPatricia Burke'], ded
    text.append('To Patricia Burke')
    note = blocks(doc['preface'])
    assert len(note) == 1 and note[0].startswith('Note—'), note
    text += ['NOTE', note[0][len('Note—'):]]  # the 1926 printings head this "NOTE"; Standard Ebooks runs it in
    for slug, head in cfg['stories']:
        b = blocks(doc[slug])
        assert len(b) > 50, slug
        text += [head] + b
    text.append(f"*** END OF THE HOSTED TEXT: {cfg['title']} ***")
    body = '\n\n'.join(text) + '\n'
    for old, new in cfg['corrections']:
        assert body.count(old) == 1, old
        body = body.replace(old, new)
    out = body.encode('utf-8')
    path = ROOT / f"data/texts/{cfg['edition']}.txt"
    path.write_bytes(out)
    sha = hashlib.sha256(out).hexdigest()
    src_path = ROOT / f"data/sources/{cfg['edition']}.json"
    rec = json.loads(src_path.read_text()) if src_path.exists() else {}
    rec.update(id=cfg['edition'], kind='public-domain-text', title=cfg['source_title'],
               sourceUrl=f"https://github.com/{cfg['repo']}/tree/{cfg['commit']}/src/epub/text",
               sourcePage=cfg['page'], sourceCommit=cfg['commit'], sourceFiles=files,
               sourceFileSha256=concat, corrections=[dict(standardEbooks=o, printed1926=n) for o, n in cfg['corrections']], sha256=sha, bytes=len(out), checked=time.strftime('%Y-%m-%d'))
    src_path.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + '\n')
    print(cfg['edition'], sha, len(out), 'source concat', concat)


if __name__ == '__main__':
    main(sys.argv[1])
