"""Load/save the hub snapshot, keeping data/catholic-hub.json and data/data.js identical."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load():return json.loads((ROOT/'data/catholic-hub.json').read_text())
def save(h):
    s=json.dumps(h,ensure_ascii=False,separators=(',',':'))
    (ROOT/'data/catholic-hub.json').write_text(s+'\n');(ROOT/'data/data.js').write_text('window.HUB_DATA='+s+';\n')
