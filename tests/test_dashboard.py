import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen
from grain_monitor.cli import simulate
from grain_monitor.dashboard import handler_for, INDEX_FILE


class DashboardTests(unittest.TestCase):
    def test_html_file_exists(self):
        self.assertTrue(INDEX_FILE.exists())
        self.assertIn("Synthetic", INDEX_FILE.read_text(encoding="utf-8"))

    def test_local_api_serves_synthetic_data(self):
        with tempfile.TemporaryDirectory() as d:
            db_path = Path(d) / "test.sqlite"
            simulate(db_path, Path(d) / "out.csv", samples=60)
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler_for(db_path))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with urlopen(f"http://127.0.0.1:{server.server_port}/api/readings", timeout=2) as response:
                    data = json.loads(response.read())
                self.assertEqual(len(data), 60)
                self.assertIn("temperature_c", data[0])
                with urlopen(f"http://127.0.0.1:{server.server_port}/api/alerts", timeout=2) as response:
                    self.assertIsInstance(json.loads(response.read()), list)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)
