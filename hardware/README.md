# Raspberry Pi 3 sensor interface (optional)

The project report describes a Raspberry Pi 3 reading a DHT temperature/humidity sensor, MQ-2 smoke/gas module, MQ-135 air-quality module and IR motion sensor. A buzzer and GSM modem are part of the proposed alerting architecture.

`raspberry_pi_readings.py` is an **untested example** of reading those sensor categories in a lab. The main Python application works without any Pi or sensors.

### Example wiring concept

| Device | Example interface | Notes |
|---|---|---|
| DHT11 | Pi GPIO4 | Report mentions DHT11; an example code fragment also mentions DHT22 |
| MQ-2 analog output | MCP3008 ADC channel 0 | Pi cannot directly read analog signals; voltage conditioning may be necessary |
| MQ-135 analog output | MCP3008 ADC channel 1 | Raw output only; not calibrated CO₂ ppm |
| IR motion sensor | Pi GPIO17 | Use 3.3 V-compatible logic or level shifting |
| Buzzer | Proposed output | Not controlled by this example |
| GSM modem | Proposed serial link | SMS sending is not implemented in this portfolio code |

Test all connections with appropriate regulated supplies, reference grounds and datasheet limits. Do **not** connect 5 V analog/logic outputs directly to Raspberry Pi GPIO, and do not treat this prototype as an operational fire or grain-spoilage safety system.

```bash
# On an appropriately configured Raspberry Pi only:
python -m pip install gpiozero adafruit-blinka adafruit-circuitpython-dht spidev
python hardware/raspberry_pi_readings.py --dht DHT11
```

Real hardware was **not** available for testing while preparing this repository. The routine only prints measurements; it does not send SMS, publish to the cloud, or switch actuators.
