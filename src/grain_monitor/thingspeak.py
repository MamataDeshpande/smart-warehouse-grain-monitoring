"""Map sensor readings to ThingSpeak fields; optional explicit upload.

A ThingSpeak write key is read from the environment, never stored in source.
The simulation and dashboard do not contact ThingSpeak by themselves.
"""

import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .models import Reading


THINGSPEAK_ENDPOINT = "https://api.thingspeak.com/update"


def make_payload(reading: Reading) -> dict[str, str]:
    """Fields matching the report's monitoring concept.

    MQ sensor outputs are arbitrary raw ADC indices, not calibrated ppm values.
    """
    return {
        "field1": f"{reading.temperature_c:.2f}",
        "field2": f"{reading.humidity_pct:.2f}",
        "field3": str(reading.mq2_raw),
        "field4": str(reading.mq135_raw),
        "field5": "1" if reading.motion else "0",
    }


def dry_run_payload(reading: Reading) -> str:
    """Inspect the payload without sending it or exposing credentials."""
    return urlencode(make_payload(reading))


def send_to_thingspeak(reading: Reading, *, write_key: str | None = None, timeout: float = 10.0) -> int:
    """Upload *one* reading after the caller explicitly requests transmission.

    Use only with a channel owned/controlled by you. ThingSpeak returns a
    positive entry ID on success, or 0 for some rejected updates.
    """
    key = write_key if write_key is not None else os.environ.get("THINGSPEAK_WRITE_KEY", "")
    if not key or not key.strip():
        raise ValueError("Set THINGSPEAK_WRITE_KEY to the write key for your own channel")
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    encoded = urlencode({"api_key": key.strip(), **make_payload(reading)}).encode("ascii")
    request = Request(
        THINGSPEAK_ENDPOINT,
        data=encoded,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    # The key is sent only in the POST body; do not log request contents.
    with urlopen(request, timeout=timeout) as response:
        result = response.read(32).decode("ascii", errors="replace").strip()
    try:
        entry_id = int(result)
    except ValueError as exc:
        raise RuntimeError("ThingSpeak returned an unexpected response") from exc
    if entry_id <= 0:
        raise RuntimeError("ThingSpeak did not accept the update")
    return entry_id
