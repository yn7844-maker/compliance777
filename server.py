"""Dependency-free, loopback-only dashboard server."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os, sys, threading, webbrowser, json
from versioning import app_version
ROOT=Path(__file__).resolve().parent
class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import unquote, urlsplit
        path=unquote(urlsplit(self.path).path)
        if path in ['/', '/index.html','/version.json']:
            version=app_version(ROOT)
            if path=='/version.json':
                content=json.dumps({'version':version}).encode();mime='application/json; charset=utf-8'
            else:
                content=(ROOT/'index.html').read_text(encoding='utf-8').replace('__APP_VERSION__',version).encode();mime='text/html; charset=utf-8'
            self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(content)));self.end_headers();self.wfile.write(content);return
        if path!='/' and not (path=='/index.html' or path.startswith(('/css/','/js/','/data/','/fonts/'))):
            self.send_error(404);return
        resolved=(ROOT/path.lstrip('/')).resolve()
        if not resolved.is_relative_to(ROOT) or (path not in ['/', '/index.html'] and not any(resolved.is_relative_to(ROOT/d) for d in ['css','js','data','fonts'])) or (path!='/' and not resolved.is_file()):
            self.send_error(404);return
        super().do_GET()
    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        super().end_headers()
if __name__=='__main__':
    os.chdir(ROOT)
    server=ThreadingHTTPServer(('127.0.0.1',8080),Handler)
    print('Dashboard: http://127.0.0.1:8080',flush=True)
    if '--no-browser' not in sys.argv: threading.Timer(.5,lambda:webbrowser.open('http://127.0.0.1:8080')).start()
    try: server.serve_forever()
    except KeyboardInterrupt: server.server_close()
