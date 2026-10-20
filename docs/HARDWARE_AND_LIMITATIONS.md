# Hardware notes and limitations

The original architecture lists a Raspberry Pi 3, DHT11, MQ-2, MQ-135, IR sensor, buzzer and GSM modem. ThingSpeak provides cloud-based visualization of sensor information. The optional [sensor example](../hardware/README.md) uses the same sensor categories, but it has **not** been tested on the original circuit.

- The report names DHT11, although one Python snippet reads a DHT22. Select the correct device and library for the hardware in use.
- MQ-2 and MQ-135 modules often expose analog outputs. A Raspberry Pi requires a separate ADC, and Pi GPIO must not receive a 5 V signal.
- MQ-135 responses depend on several gases, temperature, humidity and calibration. It should not be presented as a precise CO₂ meter without suitable characterization.
- A sensor alarm threshold is not evidence that a fire, grain spoilage or intrusion has actually occurred.
- The dashboard listens only on localhost. The ThingSpeak example sends one record only when explicitly run with `--send` and a user-owned write key.
- The original report contains an API credential. It is not part of this repository and should be rotated if still in use.

This portfolio code does not operate the GSM modem, trigger a real buzzer, or implement a production warehouse controller. It is not intended as an emergency or food-quality safety system.
