LineageOS Updater Backend
=======================
Copyright (c) 2017 The LineageOS Project<br>

Adding a new device
---
1. Add your device to devices.json, sorted alphanumerically by codename. Fields are documented below.
2. Submit your change to gerrit (this repository is configured for use with `git review`)

### devices.json
devices.json is an array of objects, each with several fields:

* `model`: should be the first thing on the line, and is the device's codename (`PRODUCT_DEVICE`) - e.g. `i9300`.
* `oem`: the manufacturer of the device. (`PRODUCT_BRAND`) - e.g. `Samsung`.
* `name`: the user-friendly name of the device - e.g. `Galaxy S III (Intl)`. Long values will overflow and look bad,
so limit this to around 25 characters.
* `has_recovery`: (*optional*) whether or not the device has a separate recovery partition. Defaults to `true`.

Development set up:
---
1. Install requirements with `pip install -r requirements.txt`
2. Copy `app.cfg.example` to `app.cfg`
3. Run with `FLASK_APP=updater.app flask run`


Example API Calls:
---
Obtaining rom list for a device:<br>
`GET /api/v1/<device>/<romtype>/<incremental>?after=<utc_timestamp>&version=<14.1>` (incremental can be anything, it is currently unused)<br>
`<device>` - Name of device. Example: `d2vzw`<br>
`<romtype>` - Type of rom. Example: `nightly`<br>
`<incremental>` - Caller device's incremental ID (ro.build.incr). Can be anything. <br>
`<after>` - Timestamp for current build on device. (optional) <br>
`<romversion>` - Version of rom. Example: `14.1`(optional)<br>


This project depends on a mirrorbits server (https://github.com/etix/mirrorbits) running our mirrorbits API (https://github.com/lineageos-infra/mirrorbits-api). Please see the README in that project for more information.
