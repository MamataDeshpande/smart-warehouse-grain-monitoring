"""Offline command-line simulation; no cloud notifications or GPIO effects."""
import argparse
import csv
import json
from pathlib import Path

from .rules import RuleEngine
from .store import connect, save_alert, save_reading
from .synthetic import sample_readings
from .thingspeak import dry_run_payload, send_to_thingspeak


def simulate(db_path: Path, csv_path: Path, samples: int = 120, seed: int = 12):
    engine = RuleEngine()
    readings = list(sample_readings(count=samples, seed=seed))
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    db = connect(db_path)
    alerts = []
    try:
        with db:
            # A demo run starts from a clean dataset for reproducible results.
            db.execute("DELETE FROM readings")
            db.execute("DELETE FROM alerts")
            for reading in readings:
                save_reading(db, reading)
                for alert in engine.evaluate(reading):
                    save_alert(db, alert)
                    alerts.append(alert)
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(vars(readings[0])))
            writer.writeheader()
            for reading in readings:
                writer.writerow(vars(reading))
    finally:
        db.close()
    return {"samples":len(readings), "alerts":len(alerts),
            "kinds":[a.kind for a in alerts], "db":str(db_path), "csv":str(csv_path)}


def main():
    parser = argparse.ArgumentParser(description="Synthetic grain warehouse monitoring demo")
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("simulate", help="Generate synthetic sensor readings and local advisory alerts")
    s.add_argument("--samples", type=int, default=120)
    s.add_argument("--seed", type=int, default=12)
    s.add_argument("--db", type=Path, default=Path("outputs/warehouse.sqlite"))
    s.add_argument("--csv", type=Path, default=Path("outputs/warehouse_readings.csv"))
    s = sub.add_parser("dashboard", help="Serve localhost-only monitoring dashboard")
    s.add_argument("--db", type=Path, default=Path("outputs/warehouse.sqlite"))
    s.add_argument("--port", type=int, default=8765)
    s = sub.add_parser("mock-cloud", help="Print the synthetic ThingSpeak fields without sending anything")
    s.add_argument("--seed", type=int, default=12)
    s = sub.add_parser("publish", help="Optionally transmit ONE example reading to your own ThingSpeak channel")
    s.add_argument("--send", action="store_true", help="Required to authorize an actual HTTP upload")
    s.add_argument("--seed", type=int, default=12)
    args = parser.parse_args()
    if args.command == "simulate":
        print(json.dumps(simulate(args.db, args.csv, args.samples, args.seed), indent=2))
    elif args.command == "dashboard":
        from .dashboard import serve
        serve(args.db, args.port)
    elif args.command == "mock-cloud":
        print(dry_run_payload(next(sample_readings(seed=args.seed))))
    elif args.command == "publish":
        reading = next(sample_readings(seed=args.seed))
        if not args.send:
            print("Dry run only. Fields:", dry_run_payload(reading))
            print("Add --send and set THINGSPEAK_WRITE_KEY to upload one record.")
        else:
            entry = send_to_thingspeak(reading)
            print(f"ThingSpeak accepted the example record as entry {entry}.")


if __name__ == "__main__":
    main()
