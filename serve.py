#!/usr/bin/env python3
"""
MBStudio91 DAW - server locale.

Serve la DAW su http://localhost:8080 e inoltra le richieste /ace/* al server
API di ACE-Step 1.5 (default http://localhost:8001), cosi' il browser non ha
problemi di CORS.

Uso:
    python serve.py                      # porta 8080, ACE-Step su :8001
    python serve.py --port 9000 --ace http://192.168.1.20:8001

Solo libreria standard di Python 3.8+, nessuna dipendenza.
"""
import argparse
import http.server
import socketserver
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREFIX = "/ace"


def make_handler(ace_url: str):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(ROOT), **kw)

        def _proxy(self, method: str):
            target = ace_url.rstrip("/") + self.path[len(PREFIX):]
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length else None
            req = urllib.request.Request(target, data=body, method=method)
            for h in ("Content-Type", "Authorization"):
                if self.headers.get(h):
                    req.add_header(h, self.headers[h])
            try:
                with urllib.request.urlopen(req, timeout=600) as r:
                    data = r.read()
                    self.send_response(r.status)
                    self.send_header("Content-Type", r.headers.get("Content-Type", "application/octet-stream"))
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
            except urllib.error.HTTPError as e:
                data = e.read()
                self.send_response(e.code)
                self.send_header("Content-Type", e.headers.get("Content-Type", "text/plain"))
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except urllib.error.URLError as e:
                msg = f"ACE-Step non raggiungibile su {ace_url}: {e.reason}".encode()
                self.send_response(502)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(msg)))
                self.end_headers()
                self.wfile.write(msg)

        def do_GET(self):
            if self.path.startswith(PREFIX + "/"):
                return self._proxy("GET")
            return super().do_GET()

        def do_POST(self):
            if self.path.startswith(PREFIX + "/"):
                return self._proxy("POST")
            self.send_error(405)

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

    return Handler


def main():
    ap = argparse.ArgumentParser(description="Server locale della MBStudio91 DAW")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--ace", default="http://localhost:8001", help="URL del server API di ACE-Step")
    args = ap.parse_args()

    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", args.port), make_handler(args.ace)) as httpd:
        print(f"MBStudio91 DAW su  http://localhost:{args.port}")
        print(f"ACE-Step inoltrato a {args.ace}  (percorso {PREFIX}/...)")
        print("Ctrl+C per fermare.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
