"""Parameterized SQLite persistence for simulated environmental data."""
import sqlite3
from pathlib import Path
from .models import Alert, Reading


def connect(path: str | Path) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(path))
    db.row_factory = sqlite3.Row
    db.executescript("""
    CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time_iso TEXT NOT NULL,
        temperature_c REAL NOT NULL,
        humidity_pct REAL NOT NULL,
        mq2_raw INTEGER NOT NULL,
        mq135_raw INTEGER NOT NULL,
        motion INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time_iso TEXT NOT NULL,
        kind TEXT NOT NULL,
        level TEXT NOT NULL,
        message TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_reading_time ON readings(time_iso);
    CREATE INDEX IF NOT EXISTS idx_alert_time ON alerts(time_iso);
    """)
    db.commit()
    return db


def save_reading(db: sqlite3.Connection, reading: Reading):
    db.execute("""INSERT INTO readings
       (time_iso, temperature_c, humidity_pct, mq2_raw, mq135_raw, motion)
       VALUES (?, ?, ?, ?, ?, ?)""",
       (reading.time_iso, reading.temperature_c, reading.humidity_pct,
        reading.mq2_raw, reading.mq135_raw, int(reading.motion)))


def save_alert(db: sqlite3.Connection, alert: Alert):
    db.execute("INSERT INTO alerts (time_iso, kind, level, message) VALUES (?,?,?,?)",
               (alert.time_iso, alert.kind, alert.level, alert.message))


def recent(db: sqlite3.Connection, table: str, limit: int = 240) -> list[dict]:
    if table not in ("readings", "alerts"):
        raise ValueError("Invalid table")
    if not 1 <= limit <= 1000:
        raise ValueError("limit out of range")
    records = db.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(x) for x in reversed(records)]
