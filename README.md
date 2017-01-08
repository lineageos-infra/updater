LineageOS Updater Backend
=======================
Copyright (c) 2017 The LineageOS Project<br>

Initial set up:
---
1. Install requirements with `pip install -r requirements.txt`
2. Copy `local_config.py.example` to `local_config.py`
3. Run with `FLASK_APP=app.py flask run`

To add entries a simple script has been added called `addrom.py`:<br>
`usage: addrom.py [-h] -f FILENAME -d DEVICE -v VERSION -dt DATETIME -t ROMTYPE -m MD5SUM`<br>
Alternatively `addon.py` can be included in another python script and the `addrom()` method can be called programatically.

Example API Calls:
--
Obtaining rom list for a device:<br>
`/api/v1/<device>/<romtype>`<br>
Request data (optional):<br>
`{"ro.build.date.utc": "<utc_timestamp>", "romversion": "<romversion>"}`<br><br>
`<device>` - Name of device. Example: `d2vzw`<br>
`<romtype>` - Type of rom. Example: `nightly`<br>
`<romversion>` - Version of rom. Example: `14.1`(optional)<br>
`<utc_timestamp>` - Timestamp for current build on device. Taken from build.prop usually. Example: `1483179136`(optional)


Requesting a file:<br>
`/api/v1/requestfile/<id>`<br>
`<id>` - Id of requested file. Obtained from json in the api call above. Example: `586bce6c07f9d87b152c3215`


TODO
====
- Lots I'm sure
