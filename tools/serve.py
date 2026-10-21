"""Local static preview. Do not use this development server for production hosting."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
parser = argparse.ArgumentParser()
parser.add_argument('--host', default='127.0.0.1')
parser.add_argument('--port', type=int, default=4173)
parser.add_argument('--strictPort', action='store_true')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
handler = partial(SimpleHTTPRequestHandler, directory=str(root))
ThreadingHTTPServer((args.host, args.port), handler).serve_forever()
