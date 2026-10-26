"""Deterministic application/catalog fingerprint, independent of Git checkout depth and build time."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPO='https://github.com/BibliothecaCatholica/bibliotheca-catholica'
def normalized_template(s):
    s=re.sub(r'<main id="main".*?</main>','<main id="main"></main>',s,flags=re.S)
    s=re.sub(r'<!-- jsonld:start -->.*?<!-- jsonld:end -->','',s,flags=re.S)
    s=re.sub(r'(<span id="gen">).*?(</span>)',r'\1\2',s)
    s=re.sub(r'(<span id="build-id">).*?(</span>)',r'\1\2',s)
    s=re.sub(r'data/site-copy\.js\?v=[0-9a-f]+','data/site-copy.js',s)
    return s
def stamp(template,snapshot):
    paths={ROOT/'app.js',ROOT/'styles.css',ROOT/'README.md'}
    for pattern in ('scripts/*.js','styles/*.css','tools/*.py','data/*.json','data/*.js'):
        paths.update(ROOT.glob(pattern))
    paths.discard(ROOT/'data/site-copy.js')  # generated from the same inputs; its cache token is normalized
    digests={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    digests['index.template']=hashlib.sha256(normalized_template(template).encode()).hexdigest()
    build='bc-'+hashlib.sha256(json.dumps(digests,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:12]
    info={'id':build,'sourceRepository':REPO,'dataSnapshot':snapshot,'note':'Content fingerprint, not a commit SHA or a claim that every record was reviewed on this date.','sha256':digests}
    (ROOT/'build.json').write_text(json.dumps(info,indent=2,sort_keys=True)+'\n')
    template=re.sub(r'(<span id="gen">).*?(</span>)',lambda m:m[1]+snapshot+m[2],template)
    template=re.sub(r'(<span id="build-id">).*?(</span>)',lambda m:m[1]+build+m[2],template)
    return template
