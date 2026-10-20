"""Simple data contracts for a synthetic grain-store monitoring demonstration."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Reading:
    time_iso: str
    temperature_c: float
    humidity_pct: float
    mq2_raw: int
    mq135_raw: int
    motion: bool


@dataclass(frozen=True)
class Alert:
    time_iso: str
    kind: str
    level: str
    message: str
