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
2. Configure your environment appropriately - see `config.py` for possible variables.
3. Supply a device_deps.json, devices.json, and optional devices_local.json. (See https://github.com/LineageOS/hudson/tree/master/updater for example) 
4. Run with `FLASK_APP=app.py flask run`


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

Don't want to run mirrorbits/mirrorbits-api?
---
Assumptions: your builds live at https://example.com/builds/. On disk, this is /data/builds/.
1. You must run this on a server with valid files. They don't need to be android builds, just make sure they have differing sha256s. and match the filename format foobar-VERSION-BUILDDATE-BUILDTYPE-DEVICE-foobar.zip.
2. Run `python gen_mirror_json.py /data/builds/ > /var/www/example.com/builds.json`.
3. Configure `UPSTREAM_URL` as `https://example.com/builds.json`.
4. Configure `DOWNLOAD_BASE_URL` as `https://example.com/builds`.
