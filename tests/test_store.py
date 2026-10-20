import tempfile
from contextlib import closing
import unittest
from pathlib import Path
from grain_monitor.models import Alert
from grain_monitor.synthetic import sample_readings
from grain_monitor.store import connect, recent, save_alert, save_reading


class StoreTests(unittest.TestCase):
    def test_store_roundtrip_and_invalid_table_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with closing(connect(Path(d) / "test.sqlite")) as db:
                reading = next(sample_readings())
                save_reading(db, reading)
                save_alert(db, Alert(reading.time_iso, "humid", "Advisory", "test only"))
                rows = recent(db, "readings")
                self.assertEqual(len(rows), 1)
                self.assertAlmostEqual(rows[0]["temperature_c"], reading.temperature_c)
                self.assertEqual(len(recent(db, "alerts")), 1)
                with self.assertRaises(ValueError):
                    recent(db, "readings; DROP TABLE readings")
                with self.assertRaises(ValueError):
                    recent(db, "readings", limit=10000)
