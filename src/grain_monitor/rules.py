"""Configurable example conditions; NOT food-storage or fire safety criteria."""
from dataclasses import dataclass

from .models import Alert, Reading


@dataclass(frozen=True)
class RuleConfig:
    # Fictitious demo values. Must not be treated as safety/food standards.
    warm_c: float = 29.0
    humid_pct: float = 74.0
    mq2_raw: int = 650
    mq135_raw: int = 570
    persistence_samples: int = 3
    clear_samples: int = 2

    def __post_init__(self):
        if self.persistence_samples < 1 or self.clear_samples < 1:
            raise ValueError("Persistence and clear sample counts must be positive")


class RuleEngine:
    """One alert per event, rearmed only after an anomaly clears.

    This intentionally suppresses repeated notifications. It does not remotely
    activate any buzzer, fan, valve or safety-critical equipment.
    """

    def __init__(self, config: RuleConfig | None = None):
        self.config = config or RuleConfig()
        self._streak = {key: 0 for key in self._keys}
        self._clear_streak = {key: 0 for key in self._keys}
        self._active = set()

    _keys = ("warm", "humid", "smoke", "air_quality", "motion")

    def evaluate(self, reading: Reading) -> list[Alert]:
        c = self.config
        conditions = {
            "warm": reading.temperature_c >= c.warm_c,
            "humid": reading.humidity_pct >= c.humid_pct,
            "smoke": reading.mq2_raw >= c.mq2_raw,
            "air_quality": reading.mq135_raw >= c.mq135_raw,
            "motion": reading.motion,
        }
        definitions = {
            "warm": ("Advisory", "Elevated temperature in simulated warehouse"),
            "humid": ("Advisory", "Elevated relative humidity in simulated warehouse"),
            "smoke": ("Warning", "Elevated mock MQ-2 signal; NOT a fire alarm"),
            "air_quality": ("Advisory", "Elevated mock MQ-135 signal; not calibrated gas concentration"),
            "motion": ("Notice", "Motion indicated by synthetic IR sensor"),
        }
        alerts: list[Alert] = []
        for key, condition in conditions.items():
            if condition:
                self._streak[key] += 1
                self._clear_streak[key] = 0
                if key not in self._active and self._streak[key] >= c.persistence_samples:
                    self._active.add(key)
                    level, message = definitions[key]
                    alerts.append(Alert(reading.time_iso, key, level, message))
            else:
                self._streak[key] = 0
                self._clear_streak[key] += 1
                if self._clear_streak[key] >= c.clear_samples:
                    self._active.discard(key)
        return alerts

    @property
    def active(self):
        return frozenset(self._active)
