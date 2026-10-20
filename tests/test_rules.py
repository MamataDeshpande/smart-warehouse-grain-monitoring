import unittest
from grain_monitor.models import Reading
from grain_monitor.rules import RuleConfig, RuleEngine


def make(time, **updates):
    defaults = dict(temperature_c=24, humidity_pct=55, mq2_raw=200, mq135_raw=200, motion=False)
    defaults.update(updates)
    return Reading(f"2026-01-01T00:00:{time:02d}+00:00", **defaults)


class RuleTests(unittest.TestCase):
    def test_no_alert_for_normal_readings(self):
        engine = RuleEngine()
        self.assertEqual([a for i in range(8) for a in engine.evaluate(make(i))], [])

    def test_persistent_temperature_triggers_once(self):
        engine = RuleEngine()
        self.assertEqual(engine.evaluate(make(0, temperature_c=33)), [])
        self.assertEqual(engine.evaluate(make(1, temperature_c=33)), [])
        alarm = engine.evaluate(make(2, temperature_c=33))
        self.assertEqual(len(alarm), 1)
        self.assertEqual(alarm[0].kind, "warm")
        self.assertEqual(engine.evaluate(make(3, temperature_c=33)), [])

    def test_anomaly_rearms_after_sustained_clear(self):
        engine = RuleEngine(RuleConfig(persistence_samples=2, clear_samples=2))
        alerts = []
        for t, temp in enumerate([35, 35, 24, 24, 35, 35]):
            alerts.extend(engine.evaluate(make(t, temperature_c=temp)))
        self.assertEqual([a.kind for a in alerts], ["warm", "warm"])

    def test_short_excursion_does_not_alert(self):
        engine = RuleEngine()
        for t, temp in enumerate([35, 24, 35, 24, 35]):
            self.assertEqual(engine.evaluate(make(t, temperature_c=temp)), [])

    def test_motion_is_a_notice(self):
        engine = RuleEngine()
        items = [a for t in range(4) for a in engine.evaluate(make(t, motion=True))]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].level, "Notice")

    def test_mq_2_does_not_claim_fire_is_detected(self):
        engine = RuleEngine()
        items = [a for t in range(4) for a in engine.evaluate(make(t, mq2_raw=900))]
        self.assertEqual(len(items), 1)
        self.assertIn("NOT a fire alarm", items[0].message)

    def test_invalid_rule_configuration(self):
        with self.assertRaises(ValueError):
            RuleConfig(persistence_samples=0)
