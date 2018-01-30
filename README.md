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
To run the server stand-alone you can use the included `docker-compose` script to bring up a simple nginx server to host your builds for you.  

### Setup
1. Place your builds in `./nginx/builds/`. These will be exposed on http://example.com/builds when you start the server. They don't need to be android builds, just make sure they have differing sha256s and match the filename format foobar-VERSION-BUILDDATE-BUILDTYPE-DEVICE-foobar.zip.
2. Run `python gen_mirror_json.py ./nginx/builds > ./nginx/builds.json`
3. Make sure you have device_deps.json, devices.json, and optional devices_local.json in the root directory of this repo.
4. Install `docker-compose` on your system.

### Building and Running
1. To build, use `docker-compose build` in the root of the repo.
2. To start the server, run `docker-compose up` in the root of the repo (include a `-d` flag to run in detached mode)
3. To stop the server, run `docker-compose down` in the root of the repo.
