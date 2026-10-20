import unittest
from grain_monitor.synthetic import sample_readings
from grain_monitor.thingspeak import make_payload, dry_run_payload


class DataTests(unittest.TestCase):
    def test_reproducible_synthetic_readings(self):
        self.assertEqual(list(sample_readings(seed=10)), list(sample_readings(seed=10)))

    def test_expected_sample_count(self):
        rows = list(sample_readings(160))
        self.assertEqual(len(rows), 160)
        self.assertTrue(all(0 <= r.humidity_pct <= 100 for r in rows))
        self.assertTrue(all(0 <= r.mq2_raw <= 1023 for r in rows))

    def test_invalid_number_of_samples(self):
        with self.assertRaises(ValueError):
            list(sample_readings(0))

    def test_cloud_payload_is_dry_run_and_has_no_key(self):
        sample = next(sample_readings())
        payload = make_payload(sample)
        self.assertEqual(set(payload), {"field1", "field2", "field3", "field4", "field5"})
        fragment = dry_run_payload(sample)
        self.assertIn("field1=", fragment)
        self.assertNotIn("api_key", fragment.lower())
