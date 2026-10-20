# Academic project background

The Intelligent Grain Storage Management System project investigated how IoT could make warehouse environmental conditions easier to monitor. The report described a Raspberry Pi 3 connected to a DHT11 temperature/humidity sensor, MQ-2 smoke sensor, MQ-135 gas sensor and an IR movement detector. It proposed local and remote views of the data using ThingSpeak, a desktop system, a mobile application and alerting hardware.

The central purpose was to give warehouse staff a quicker indication of environmental problems that could affect stored grain.

## About this repository

This version follows the report's architecture and keeps the core sensor/monitoring functions. Its software has been updated and reorganized for Python 3. A simulator, SQLite storage, a localhost dashboard and tests have been added so the project can be explored without hardware.

The report documents prototype sensor/ThingSpeak work, but it does not establish that the full Android, GSM and automated control concepts were completed and validated. This repository does not claim those features are operational.

The report's historical ThingSpeak API key is not included in this source tree. Anyone reusing an earlier channel should replace its write key before configuring new uploads.
