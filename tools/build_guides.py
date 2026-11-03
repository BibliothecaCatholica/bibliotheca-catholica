"""Write data/guides.js (window.GUIDES) from tools/guide_pages.py, for the app's #/guides/<slug> route.
tools/build_static.py pre-renders the same HTML at /guides/<slug>/. Run by `npm run build`."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'));import guide_pages
def main():
    P=guide_pages.pages()
    (ROOT/'data/guides.js').write_text('window.GUIDES='+json.dumps({k:{'title':v['title'],'html':v['html']} for k,v in P.items()},ensure_ascii=False,separators=(',',':'))+';\n')
    print(len(P),'guides')
if __name__=='__main__':main()
