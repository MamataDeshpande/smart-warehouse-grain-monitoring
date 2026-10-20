"""Deterministic synthetic readings; not actual grain conditions or sensor calibrations."""
from datetime import datetime, timedelta, timezone
import math
import random

from .models import Reading


def sample_readings(count: int = 120, seed: int = 12, interval_s: int = 60):
    """Simulate normal fluctuations and separate warm/humid/gas/motion events."""
    if count < 1 or interval_s < 1:
        raise ValueError("count and interval_s must be positive")
    rng = random.Random(seed)
    start = datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc)
    for i in range(count):
        temp = 23 + 0.9 * math.sin(i / 12) + rng.gauss(0, 0.20)
        humidity = 56 + 3.5 * math.sin(i / 14) + rng.gauss(0, 0.9)
        smoke = int(155 + rng.gauss(0, 14))
        air = int(225 + rng.gauss(0, 20))
        motion = False
        # Demonstration events only; unrelated to physical sensor response curves.
        if count // 5 <= i < count // 5 + max(5, count // 9):
            temp += 8.0
            humidity += 23.0
        if count // 2 <= i < count // 2 + max(5, count // 10):
            smoke += 630
            air += 390
        if 4 * count // 5 <= i < 4 * count // 5 + 4:
            motion = True
        yield Reading(
            time_iso=(start + timedelta(seconds=i * interval_s)).isoformat(),
            temperature_c=round(temp, 2),
            humidity_pct=round(max(0, min(100, humidity)), 2),
            mq2_raw=max(0, min(1023, smoke)),
            mq135_raw=max(0, min(1023, air)),
            motion=motion,
        )
