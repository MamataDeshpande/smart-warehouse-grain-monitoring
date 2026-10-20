"""ThingSpeak upload behavior is tested with an in-memory mocked HTTP call."""
import io
import os
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs

from grain_monitor.synthetic import sample_readings
from grain_monitor.thingspeak import send_to_thingspeak


class MockResponse:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size):
        return b"42"


class ThingSpeakTests(unittest.TestCase):
    def test_refuses_upload_without_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                send_to_thingspeak(next(sample_readings()))

    def test_upload_is_post_and_does_not_put_key_in_url(self):
        sample = next(sample_readings())
        with patch("grain_monitor.thingspeak.urlopen", return_value=MockResponse()) as urlopen:
            result = send_to_thingspeak(sample, write_key="EXAMPLE_PLACEHOLDER_ONLY")
        self.assertEqual(result, 42)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_method(), "POST")
        self.assertNotIn("EXAMPLE_PLACEHOLDER_ONLY", request.full_url)
        body = parse_qs(request.data.decode("ascii"))
        self.assertEqual(body["api_key"], ["EXAMPLE_PLACEHOLDER_ONLY"])
        self.assertEqual(body["field1"], [f"{sample.temperature_c:.2f}"])


if __name__ == "__main__":
    unittest.main()
