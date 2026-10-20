"""Optional Raspberry Pi 3 hardware sensor bridge (not tested on real hardware).

Install gpiozero, adafruit-blinka, adafruit-circuitpython-dht, spidev
on a Raspberry Pi before use. Pin/voltage assignments are EXAMPLES ONLY.
See docs/HARDWARE_AND_LIMITATIONS.md and verify wiring against datasheets.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone


def read_once(*, sensor_type: str = "DHT11") -> dict:
    """Collect one set of example sensor readings from authorized lab hardware.

    ADXL/MQ readings are not calibrated environmental measurements.
    Requires a separately wired MCP3008 ADC for MQ-2 and MQ-135 analog outputs.
    """
    try:
        import board  # type: ignore
        import adafruit_dht  # type: ignore
        from gpiozero import DigitalInputDevice, MCP3008  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Raspberry Pi sensor libraries are missing. See hardware/README.md"
        ) from exc

    if sensor_type not in {"DHT11", "DHT22"}:
        raise ValueError("sensor_type must be DHT11 or DHT22")

    dht_class = adafruit_dht.DHT11 if sensor_type == "DHT11" else adafruit_dht.DHT22
    dht = dht_class(board.D4, use_pulseio=False)
    mq2, mq135 = MCP3008(channel=0), MCP3008(channel=1)
    pir = DigitalInputDevice(17)
    try:
        # Raw scaled ADC value only: NOT ppm, not a certified fire indicator.
        temperature = dht.temperature
        humidity = dht.humidity
        if temperature is None or humidity is None:
            raise RuntimeError("No valid DHT reading; retry after checking wiring")
        return {
            "time_iso": datetime.now(timezone.utc).isoformat(),
            "temperature_c": float(temperature),
            "humidity_pct": float(humidity),
            "mq2_raw": round(mq2.value * 1023),
            "mq135_raw": round(mq135.value * 1023),
            "motion": bool(pir.value),
        }
    finally:
        dht.exit()
        mq2.close()
        mq135.close()
        pir.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Read example Pi-connected sensors once")
    parser.add_argument("--dht", choices=["DHT11", "DHT22"], default="DHT11")
    args = parser.parse_args()
    print(json.dumps(read_once(sensor_type=args.dht), indent=2))


if __name__ == "__main__":
    main()
