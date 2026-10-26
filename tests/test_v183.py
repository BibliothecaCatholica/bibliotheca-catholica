"""v18.3: EWTN News replaces the redirected Catholic News Agency link; Gregory the Great's catalog dates corrected."""
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=lambda p:(ROOT/p).read_text(encoding='utf-8')
class V183(unittest.TestCase):
    def test_ewtn_news_link(self):
        for p in ['data/catholic-hub.json','data/data.js','media/index.html','tools/resources.py']:
            with self.subTest(p):
                s=R(p);self.assertNotIn('catholicnewsagency.com',s);self.assertIn('https://www.ewtnnews.com/',s);self.assertIn('EWTN News',s)
    def test_gregory_dates(self):
        hub=json.loads(R('data/catholic-hub.json'));A={a['id']:a for a in hub['authors']}
        self.assertEqual((A['gregory-the-great']['born'],A['gregory-the-great']['died']),(540,604))
        self.assertEqual((A['benedict-of-nursia']['born'],A['benedict-of-nursia']['died']),(480,547))
        g=next(i for i in hub['isidore'] if i['f']==A['gregory-the-great']['isidoreFolder'])
        self.assertEqual(g['n'],'Gregory the Great, Pope St., O.S.B. (c. 540-604)')
        books=json.loads(R('data/books.json'))
        names=[n for n,i in books['authors'] if i=='gregory-the-great']
        self.assertIn('Gregory the Great, Pope St., O.S.B. (c. 540-604)',names)
        self.assertFalse(any('Gregory' in n and '480-547' in n for n,_ in books['authors']))
        # the only place the old string stays is the folder's actual name on isidore.co (folder lists and the open data folder column)
        for p in ['author/gregory-the-great/index.html','data/open/isidore-index.csv','data/open/authors.csv','data/data.js']:
            with self.subTest(p):self.assertEqual(R(p).count('O.S.B. (480-547)'),R(p).count('"isidoreFolder":"Gregory the Great, Pope St., O.S.B. (480-547)"')+R(p).count('"f":"Gregory the Great, Pope St., O.S.B. (480-547)"'))
        self.assertIn('author=Gregory%20the%20Great%2C%20Pope%20St.%2C%20O.S.B.%20%28c.%20540-604%29',R('author/gregory-the-great/index.html'))
        self.assertIn('from catalog_fixes import',R('tools/build_books.py'))
if __name__=='__main__':unittest.main()
