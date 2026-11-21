#!/usr/bin/env python3
"""Validate the chapter and story maps in tools/text_pages.py and write data/text-pages.json/.js.

For each hosted edition: the file's SHA-256 must equal the edition's `sha256` in data/library.json,
every heading must occur exactly once after `start_after`, in order, and each part's first and last
paragraphs must start and end with the words Research mapped. A part runs from its heading block to
the block before the next heading (a bare Roman numeral printed above a heading is left out); the
last part ends before the Project Gutenberg (or hosted-text) END marker. Part of `npm run build`.

    python3 tools/build_text_pages.py
"""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import text_pages as TP
from reader_formatting import structure_for
SIZE=35  # reader section size (read() in scripts/library.js)
SLUG=re.compile(r'^\d\d-[a-z0-9]+(?:-[a-z0-9]+)*$')
def split_text(raw):
    """Same as splitText() in scripts/library.js: blank-line blocks, trimmed, empties dropped."""
    return [p.strip() for p in re.split(r'\n\s*\n',raw.replace('\r','')) if p.strip()]
def norm(s):return re.sub(r'\s+',' ',s).strip().casefold()
def words(s):return len(re.sub(r'[_\[\]]',' ',s).split())
# Part D, "Beautiful editions" (owner brief; Orthodoxy pilot, November 14-15, 2026): editions presented as designed
# books: a title-page work page (facts line, three choices, About this edition), chapter openers and endings.
PART_D={
    'orthodoxy':{'about':'Project Gutenberg #130: the 1908 first edition text, with Chesterton’s Preface. The nine chapters and the title page follow Gutenberg’s own HTML for the same eBook, matched word for word with the hosted text; no words were changed.'},
    # Batch 1 (November 15, 2026). Each sentence restates the edition's own record in data/library.json and its map.
    'story-of-a-soul':{'about':'Project Gutenberg #16772: the Thomas N. Taylor translation, with the additional writings and sayings of his edition. The eleven chapters of the autobiography follow Gutenberg’s own HTML for the same eBook, matched with the hosted text; no words were changed.'},
    'innocence-father-brown':{'about':'Project Gutenberg #204: the first Father Brown collection, twelve stories. Story divisions follow the site’s map of the hosted text; no words were changed.'},
    'wisdom-father-brown':{'about':'Project Gutenberg #223: the second collection, first published in 1914 (London: Cassell), twelve stories. Story divisions follow the site’s map of the hosted text; no words were changed.'},
    'secret-father-brown':{'about':'Project Gutenberg #70175: first published in 1927 (London: Cassell and Company), eight stories between an opening and a closing frame story. Story divisions follow the site’s map of the hosted text; no words were changed.'},
    'incredulity-father-brown':{'about':'The Standard Ebooks text (CC0), corrected to the wording of the 1926 Cassell printings, eight stories. Each correction is listed in the edition’s provenance record. Story divisions follow the site’s map of the hosted text.'},
    # Batch 2 (November 15, 2026). Each sentence restates the edition's record in data/library.json and its map.
    'heretics':{'about':'Project Gutenberg #470: first published in 1905 (John Lane); the transcription follows the twelfth edition (John Lane Company, New York, 1919). Twenty chapters, divided as the hosted text heads them; no words were changed.'},
    'ball-and-cross':{'about':'Project Gutenberg #5265: first published in 1909 (New York: John Lane; London: Wells Gardner, Darton, 1910). Twenty chapters, divided as the hosted text heads them; no words were changed.'},
    'man-thursday':{'about':'Project Gutenberg #1695: The Man Who Was Thursday: A Nightmare. Fifteen chapters, divided as the hosted text heads them; no words were changed.'},
    'chesterton-francis':{'about':'Project Gutenberg #63084: St. Francis of Assisi. Ten chapters, divided as the hosted text heads them; the publisher’s list that follows stays in the reader. No words were changed.'},
    'grammar-assent':{'about':'Project Gutenberg #34022: ten chapters in two parts, divided as the hosted text heads them; the notes at the end stay with the last chapter. No words were changed.'},
    'development-doctrine':{'about':'Project Gutenberg #35110: twelve chapters in two parts, divided as the hosted text heads them; the introduction stays in the reader. No words were changed.'},
    'paradoxes-catholicism':{'about':'Project Gutenberg #16309: sermons preached in England, New York (Lent 1912), and Rome (Lent 1913), published in 1913 (London: Longmans, Green). Eleven chapters, divided as the hosted text heads them; the introduction stays in the reader. No words were changed.'},
    'life-of-teresa':{'about':'Project Gutenberg #8120: the autobiography in David Lewis’s translation. Forty chapters, divided as the hosted text heads them, each titled by the first line of its summary; the prologue and the Relations stay in the reader. No words were changed.'},
    'apologia':{'about':'Project Gutenberg #19690: seven parts, divided as the hosted text heads them; the Postscriptum stays in the reader. No words were changed.'},
    'virgin-saints-and-martyrs':{'about':'Project Gutenberg #53841: Gutenberg’s title page names Thomas Y. Crowell & Co., New York, 1901; illustrations by F. Anger. Eighteen lives, divided as the hosted text heads them; each plate caption stays in the reader. No words were changed.'},
    # Chesterton editions (November 15, 2026). Each sentence restates the edition's record and its map.
    'catholic-church-conversion':{'about':'Project Gutenberg #76305: the Macmillan, New York printing of 1927 in the Calvert Series. Six chapters, divided as the hosted text heads them; no words were changed.'},
    'ballad-white-horse':{'about':'Project Gutenberg #1719: first published in 1911 (London: Methuen). Eight books, divided as the hosted text heads them; the dedication stays in the reader. No words were changed.'},
    'whats-wrong-world':{'about':'Project Gutenberg #1717: first published in 1910. Forty-six chapters in five parts and three closing notes, divided as the hosted text heads them; the dedication stays in the reader. No words were changed.'},
    'manalive':{'about':'Project Gutenberg #1718: the Thomas Nelson and Sons text of 1912. Ten chapters in two parts, divided as the hosted text heads them; no words were changed.'},
    'club-queer-trades':{'about':'Project Gutenberg #1696: first published in 1905. Six stories, divided as the hosted text heads them; no words were changed.'},
    'short-history-england':{'about':'Project Gutenberg #20897: first published in 1917; transcribed from a Chatto & Windus, London printing. Eighteen chapters, divided as the hosted text heads them; no words were changed.'},
    'man-who-knew-too-much':{'about':'Project Gutenberg #1720: first published in 1922. Eight Horne Fisher stories, divided as the hosted text heads them; no words were changed.'},
    'flying-inn':{'about':'Project Gutenberg #59239: the John Lane Company, New York printing (copyright 1914). Twenty-five chapters, divided as the hosted text heads them; no words were changed.'},
    'trees-of-pride':{'about':'Project Gutenberg #1721: first published in 1922. Four chapters, divided as the hosted text heads them; no words were changed.'},
    # Orthodoxy flow batch 1 (November 19, 2026). Each sentence restates the edition's record and its map.
    'confessions':{'about':'Project Gutenberg #3296: the translation by E. B. Pusey. Thirteen books, divided as the hosted text heads them; no words were changed.'},
    'betrothed':{'about':'Project Gutenberg #35155: the English translation published in London by Richard Bentley in 1834 (Standard Novels). Thirty-seven chapters, divided as the hosted text heads them; the transcriber’s note stays in the reader. No words were changed.'},
    'revelations-divine-love':{'about':'Project Gutenberg #52958: Grace Warrack’s version (London: Methuen, 1901). Julian’s eighty-six chapters, divided as the hosted text heads them; Warrack’s introduction stays in the reader. No words were changed.'},
    # Orthodoxy flow batch 2 (November 19, 2026). Each sentence restates the edition's record and its map.
    'bede-ecclesiastical-history':{'about':'Project Gutenberg #38326: A. M. Sellar’s revised translation (London: George Bell and Sons, 1907). Five books, divided as the hosted text heads them; the preface, index, and footnotes stay in the reader. No words were changed.'},
    'consolation-philosophy':{'about':'Project Gutenberg #14328: H. R. James’s translation (London: Elliot Stock, 1897). Five books, each with its summary, songs, and prose, divided as the hosted text heads them; the introduction, epilogue, and notes stay in the reader. No words were changed.'},
    'abandonment':{'about':'Project Gutenberg #52057: Ella McMahon’s translation, edited by H. Ramière (New York: Benziger Brothers, 1887). Thirty-three chapters in three books, divided as the hosted text heads them; the appendix of prayers stays in the reader. No words were changed.'},
    # Orthodoxy flow batch 3 (November 20, 2026). Each sentence restates the edition's record and its map.
    'catherine-letters':{'about':'Project Gutenberg #7403: Vida D. Scudder’s translation and selection (1905). Sixty letters in the book’s sections, divided as the hosted text heads them, each with the editor’s note that introduces it; the introduction and tables stay in the reader. No words were changed.'},
    'apostolic-fathers':{'about':'Project Gutenberg #77576: the Ante-Nicene Christian Library, vol. I (Edinburgh: T. & T. Clark, 1870). Twenty-two parts, one for each writing as the volume heads it, with its introductory notice; the indexes stay in the reader. No words were changed.'},
    'europe-faith':{'about':'Project Gutenberg #8442: Hilaire Belloc’s Europe and the Faith. The Introduction and ten chapters, divided as the hosted text heads them; no words were changed.'},
    # Orthodoxy flow batch 4 (November 20, 2026). Each sentence restates the edition's record and its map.
    'idea-university':{'about':'Project Gutenberg #24526: Newman’s The Idea of a University. Nine discourses and ten lectures and essays, divided as the hosted text heads them; the preface, index, and notes stay in the reader. No words were changed.'},
    'aquinas-prayer-contemplative':{'about':'Project Gutenberg #22295: Hugh Pope’s translation (London: R. & T. Washbourne, 1914). Nine questions from the Summa, divided as the hosted text heads them; the introduction and indexes stay in the reader. No words were changed.'},
    'glories-of-mary':{'about':'Project Gutenberg #72411: the second American edition (New York: Edward Dunigan and Brother, 1852). Ten chapters on the Salve Regina, nine discourses, and the devotions that follow, divided as the hosted text heads them; the footnotes stay in the reader. No words were changed.'},
    # Councils Part 3 (November 20, 2026). The sentence restates the edition's record and its map.
    'council-of-trent':{'about':'J. Waterworth’s translation (London: C. Dolman, 1848), in the Hanover Historical Texts transcription served by Papal Encyclicals Online. The bull of indiction and the twenty-five sessions, each headed by its source page’s own title; the preface and the transcribers’ notes stay in the reader. No words were changed.'},
    # Chesterton polish batch 1 (November 21, 2026). Each sentence restates the edition's record and its map.
    'everlasting-man':{'about':"Project Gutenberg #65688: the Hodder and Stoughton, London text, printed by T. and A. Constable. The introduction, fourteen chapters in two parts, the conclusion, and two appendices, divided as the hosted text heads them; the prefatory note and the transcriber's note stay in the reader. No words were changed."},
    'tremendous-trifles':{'about':'Project Gutenberg #8092: first published in 1909. Thirty-nine essays, divided as the hosted text heads them; no words were changed.'},
    'new-jerusalem':{'about':'Project Gutenberg #13468: first published in 1920. Thirteen chapters and the conclusion, divided as the hosted text heads them; the preface stays in the reader. No words were changed.'},
    # Chesterton polish batch 2 (November 21, 2026). Each sentence restates the edition's record and its map.
    'charles-dickens-critical-study':{'about':'Project Gutenberg #68682: first published in 1906; the transcribed copy is the Dodd, Mead & Company, New York printing of 1911. Twelve chapters, divided as the hosted text heads them; no words were changed.'},
    'poet-and-lunatics':{'about':'Project Gutenberg Australia #0900711: first published in 1929. Eight stories of Gabriel Gale, divided as the hosted text heads them; no words were changed.'},
    'return-don-quixote':{'about':'Project Gutenberg Australia #0900401: first published in 1927. Nineteen chapters, divided as the hosted text heads them; no words were changed.'},
    # Chesterton polish batch 3 (November 21, 2026). Each sentence restates the edition's record and its map.
    'william-cobbett':{'about':'Project Gutenberg Australia #0900441: first published in 1925. Seven chapters, divided as the hosted text heads them; no words were changed.'},
    'robert-louis-stevenson-1927':{'about':'Project Gutenberg Australia #0900631: first published in 1927. Ten chapters, divided as the hosted text heads them; no words were changed.'},
    'irish-impressions':{'about':'Project Gutenberg #61758: first published in 1919; the transcribed copy is the second impression (Collins, London, January 1920). Nine chapters, divided as the hosted text heads them; no words were changed.'},
    # Chesterton polish batch 4 (November 21, 2026). Each sentence restates the edition's record and its map.
    'napoleon-notting-hill':{'about':'Project Gutenberg #20058: first published in 1904; the transcribed copy is the John Lane: The Bodley Head printing of 1904. Fifteen chapters in five books, divided as the hosted text heads them; the dedication and the list of illustrations stay in the reader. No words were changed.'},
    'victorian-age-literature':{'about':'Project Gutenberg #18639: first published in 1913; the transcribed copy is a Home University Library printing (New York and London). Four chapters, divided as the hosted text heads them; no words were changed.'},
    'four-faultless-felons':{'about':'Project Gutenberg Australia #0300781: first published in 1930. The prologue and four stories of six chapters each, divided as the hosted text heads them; no words were changed.'},
    # Chesterton polish batch 5 (November 21, 2026). Each sentence restates the edition's record and its map.
    'eugenics-other-evils':{'about':'Project Gutenberg #25308: first published in 1922; the transcribed copy is the Cassell and Company printing of 1922. Seventeen chapters in two parts, divided as the hosted text heads them; the note to the reader stays in the reader. No words were changed.'},
    'tales-long-bow':{'about':'Project Gutenberg #69185: first published in 1925; the transcribed copy is the Dodd, Mead and Company, New York printing. Eight tales, divided as the hosted text heads them; no words were changed.'},
    # Douay-Rheims Wisdom and Ecclesiasticus (November 21, 2026). Each sentence restates the edition's record and its map.
    'book-of-wisdom-douay-rheims':{'about':"eBible.org's transcription of the Douay-Rheims American edition of 1899: the nineteen chapters of the Book of Wisdom, each verse a paragraph with its number."},
    'ecclesiasticus-douay-rheims':{'about':"eBible.org's transcription of the Douay-Rheims American edition of 1899: the fifty-one chapters of Ecclesiasticus, each verse a paragraph with its number."},
}
def part_d(wid,d):
    """Facts for the title page: total words of the parts (rounded to the thousand) and reading time at 230 words a minute."""
    wc=sum(x['words'] for x in d['items'])
    return dict(PART_D[wid],words=wc,minutes=round(wc/230))
def items_for(wid,spec,B):
    """The parts of one mapped work: heading, body range, and words (also used by tools/structure_text.py map mode).

    A heading is one block, or a tuple of consecutive blocks (a numeral line and a title line); the whole tuple must occur
    once, unless it is given as {'text': heading, 'occurrence': n}: the n-th time that heading occurs after
    `start_after`, for a book that prints the same heading more than once ("TO GREGORY XI" in Catherine's letters). `divisions` (optional) are exact texts of headings that stand between parts ("PART II.", a plate caption printed
    before the next chapter): they are left out of the part before them, recorded as that next part's `before` blocks,
    and kept in the reader and the EPUB."""
    end=next(i for i,b in enumerate(B) if re.search(r'\*\*\* ?END OF (THE |THIS )?(PROJECT GUTENBERG|HOSTED TEXT)',b,re.I))
    at=next(i for i,b in enumerate(B) if norm(b)==norm(spec['start_after']))
    # back matter after the last part: the first match after start_after (a contents list may print the same words earlier)
    if spec.get('end_before'):end=next(i for i in range(at+1,len(B)) if norm(B[i])==norm(spec['end_before']))
    div={norm(x) for x in spec.get('divisions',())}
    heads=[]
    for slug,num,title,head,first,last in spec['parts']:
        assert SLUG.match(slug) and len(slug)<=60,slug  # page paths keep each segment under 80 characters
        nth=None
        if isinstance(head,dict):head,nth=head['text'],head['occurrence']  # a heading the book prints more than once
        hs=head if isinstance(head,tuple) else (head,)
        hits=[i for i in range(at+1,end) if all(i+j<end and norm(B[i+j])==norm(x) for j,x in enumerate(hs))]
        if nth is None:assert len(hits)==1,(wid,slug,'heading must occur once',hits)
        else:assert nth>=1 and len(hits)>=nth,(wid,slug,'occurrence',nth,hits);hits=[hits[nth-1]]
        assert not heads or hits[0]>heads[-1][0],(wid,slug,'out of order')
        heads.append((hits[0],len(hs)))
    items=[];prev_end=None
    for k,(slug,num,title,head,first,last) in enumerate(spec['parts']):
        h,n=heads[k];stop=(heads[k+1][0] if k+1<len(heads) else end)-1
        while stop>h and (re.fullmatch(r'[IVXLC]+\.?',B[stop]) or norm(B[stop]) in div):stop-=1  # a numeral or a division printed above the next heading
        body=list(range(h+n,stop+1))
        assert body,(wid,slug,'empty part')
        assert norm(B[body[0]]).startswith(norm(first)),(wid,slug,'first words do not match',B[body[0]][:80])
        assert norm(B[body[-1]]).endswith(norm(last)),(wid,slug,'last words do not match',B[body[-1]][-80:])
        before=[i for i in range(prev_end+1,h) if norm(B[i]) in div] if prev_end is not None and div else []
        items.append(dict(slug=slug,num=num,title=title,heading=h,start=body[0],end=body[-1],section=h//SIZE,
                          words=sum(words(B[i]) for i in body),firstWords=' '.join(re.sub(r'[_]','',B[body[0]]).split()[:12]),
                          **({'titleBlocks':list(range(h+1,h+n))} if n>1 else {}),**({'before':before} if before else {})))
        prev_end=body[-1]
    return items
def build():
    lib=json.loads((ROOT/'data/library.json').read_text());works={w['id']:w for w in lib['works']}
    flags=json.loads((ROOT/'data/editorial-flags.json').read_text())
    out={}
    for wid,spec in TP.WORKS.items():
        w=works[wid];e=next(x for x in w['editions'] if x['id']==spec['edition'])
        assert e.get('text') and e.get('sha256'),(wid,'not a hosted edition')
        src=json.loads((ROOT/('data/sources/'+e['id']+'.json')).read_text())
        # Gutenberg editions, or (2026-11-09, The Incredulity of Father Brown) a public-domain text with a provenance record
        assert 'gutenberg.org' in e['source'] or src.get('kind')=='public-domain-text',(wid,'chapter pages need a Gutenberg or provenance-checked edition')
        assert not w.get('authorId') or w['authorId'] not in flags.get('hubAuthors',[]),wid
        raw=(ROOT/e['text']).read_bytes();assert hashlib.sha256(raw).hexdigest()==e['sha256'],(wid,'text changed')
        B=split_text(raw.decode('utf-8'))
        items=items_for(wid,spec,B)
        assert len({i['slug'] for i in items})==len(items),wid
        st=structure_for(e)  # structured-text pilot (tools/structure_text.py): roles, only for this exact TXT
        if st:
            S=json.loads((ROOT/st['source']).read_text())
            assert [(c['heading'],c['start'],c['end']) for c in S['chapters']]==[(x['heading'],x['start'],x['end']) for x in items],(wid,'structure and chapter map disagree')
        out[wid]=dict(**({'partD':part_d(wid,{'items':items})} if wid in PART_D else {}),edition=e['id'],kind=spec['kind'],editionLine=spec.get('edition_line',''),noun=spec['noun'],nouns=spec['nouns'],sha256=e['sha256'],blocks=len(B),items=items,**({'structure':st} if st else {}))
    return out
def main():
    data=build()
    (ROOT/'data/text-pages.json').write_text(json.dumps({'note':'Generated by tools/build_text_pages.py from tools/text_pages.py; block indexes are splitText() blocks of the hosted file.','works':data},ensure_ascii=False,indent=1)+'\n')
    slim={wid:dict({'edition':d['edition'],'k':d['kind'],'n':d['nouns'],'i':[[x['slug'],x['num'],x['title'],x['heading']]+([x['end']] if d.get('partD') else []) for x in d['items']]},**({'d':d['partD']} if d.get('partD') else {}),**({'s':dict({'sha256':d['structure']['sha256'],'r':d['structure']['roles']},**({'f':d['structure']['front']} if d['structure'].get('front') else {}))} if d.get('structure') else {})) for wid,d in data.items()}
    (ROOT/'data/text-pages.js').write_text('window.TEXT_PAGES='+json.dumps(slim,ensure_ascii=False,separators=(',',':'))+';\n')
    print('text pages:',', '.join('%s %d'%(k,len(v['items'])) for k,v in data.items()))
if __name__=='__main__':main()
