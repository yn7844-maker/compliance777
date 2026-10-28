"""Dependency-free, loopback-only dashboard server."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os, sys, threading, webbrowser
ROOT=Path(__file__).resolve().parent
class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import unquote, urlsplit
        path=unquote(urlsplit(self.path).path)
        if path!='/' and not (path=='/index.html' or path.startswith(('/css/','/js/','/data/'))):
            self.send_error(404);return
        resolved=(ROOT/path.lstrip('/')).resolve()
        if not resolved.is_relative_to(ROOT) or (path not in ['/', '/index.html'] and not any(resolved.is_relative_to(ROOT/d) for d in ['css','js','data'])) or (path!='/' and not resolved.is_file()):
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
