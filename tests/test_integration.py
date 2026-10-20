import csv
import tempfile
from contextlib import closing
import unittest
from pathlib import Path
from grain_monitor.cli import simulate
from grain_monitor.store import connect, recent


class EndToEndTests(unittest.TestCase):
    def test_simulation_creates_fictional_readings_and_advisories(self):
        with tempfile.TemporaryDirectory() as d:
            db_path, csv_path = Path(d)/"test.sqlite", Path(d)/"readings.csv"
            result = simulate(db_path, csv_path, samples=120)
            self.assertEqual(result["samples"], 120)
            self.assertTrue(csv_path.exists())
            self.assertGreater(result["alerts"], 0)
            with closing(connect(db_path)) as db:
                self.assertEqual(len(recent(db, "readings")), 120)
                self.assertEqual(len(recent(db, "alerts")), result["alerts"])
            with csv_path.open() as f:
                self.assertEqual(len(list(csv.DictReader(f))), 120)

    def test_second_run_replaces_old_demo(self):
        with tempfile.TemporaryDirectory() as d:
            db_path, csv_path = Path(d)/"test.sqlite", Path(d)/"readings.csv"
            simulate(db_path, csv_path, samples=120)
            simulate(db_path, csv_path, samples=100, seed=25)
            with closing(connect(db_path)) as db:
                self.assertEqual(len(recent(db, "readings")), 100)
