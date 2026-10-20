"""Read-only web dashboard limited to localhost, no external dependencies."""
import json
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .store import connect, recent

INDEX_FILE = Path(__file__).resolve().parents[2] / "web" / "index.html"


def handler_for(db_path: Path, html_path: Path = INDEX_FILE):
    class DashboardHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            route = urlparse(self.path).path
            if route == "/":
                payload = html_path.read_bytes()
                ctype = "text/html; charset=utf-8"
            elif route in ("/api/readings", "/api/alerts"):
                with closing(connect(db_path)) as db:
                    rows = recent(db, route.split("/")[-1])
                payload = json.dumps(rows).encode("utf-8")
                ctype = "application/json; charset=utf-8"
            else:
                self.send_error(404, "Not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline' 'self'; script-src 'self' 'unsafe-inline'")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format, *args):
            return  # avoid noisy trace of polling
    return DashboardHandler


def serve(db_path: Path, port: int = 8765):
    if not 1024 <= port <= 65535:
        raise ValueError("Port must be between 1024 and 65535")
    db_path = Path(db_path)
    with ThreadingHTTPServer(("127.0.0.1", port), handler_for(db_path)) as server:
        print(f"Local dashboard: http://127.0.0.1:{port}")
        print("For demonstration only; no real sensors or external network communication.")
        server.serve_forever()
