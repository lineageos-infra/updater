LineageOS Updater Backend
=======================
Copyright (c) 2017 The LineageOS Project<br>

Adding a new device
---
1. Add your device to devices.json, sorted alphanumerically by codename. Fields are documented below.
2. Add a 109x124 PNG of your device to the static/device folder
3. Submit your change to gerrit (this repository is configured for use with `git review`)

### devices.json
devices.json is an array of objects, each with several fields:

* `model`: should be the first thing on the line, and is the device's codename (`PRODUCT_DEVICE`) - e.g. `i9300`.
* `oem`: the manufacturer of the device. (`PRODUCT_BRAND`) - e.g. `Samsung`.
* `name`: the user-friendly name of the device - e.g. `Galaxy S III (Intl)`. Long values will overflow and look bad,
so limit this to around 25 characters.
* `has_recovery`: (*optional*) whether or not the device has a separate recovery partition. Defaults to `true`.
* `image`: (*optional*) the filename (excluding .png) of the device's image. Defaults to the value of `model`.
* `wiki`: (*optional*) the name of the wiki page, excluding "\_info". Defaults to the value of `model`.
For example, `i9300` would be shown on the website as a link to http://wiki.lineageos.org/i9300_info.html.

This file is no longer read from disk by the application and must be loaded into mongo. To do so, run: 

`FLASK_APP=app.py flask import_devices`

Initial set up:
---
1. Install requirements with `pip install -r requirements.txt`
2. Copy `app.cfg.example` to `app.cfg`
3. Import the devices list with `FLASK_APP=app.py flask import_devices`
4. Run with `FLASK_APP=app.py flask run`


API Keys
---
Any method with the `@api_key_required` decorate requires an API key. You can generate one by running: <br>
`FLASK_APP=app.py flask api_key [OPTIONS]"` <br>

```
Options:
  --comment TEXT
  --remove TEXT
  --print
  --help          Show this message and exit.
```

Adding and removing entries:
---
To add use `FLASK_APP=app.py flask addrom [OPTIONS]`

```
Options:
  -f, --filename TEXT   [required] (Example: lineage-14.1-20170114-NIGHTLY-v500.zip)
  -d, --device TEXT     [required] (Example: v500)
  -v, --version TEXT    [required] (Example: 14.1)
  -t, --datetime TEXT   [required] (Example: "2017-01-14 13:59:25")
  -r, --romtype TEXT    [required] (Example: nightly)
  -m, --md5sum TEXT     [required] (Example: 0f80ec88915e8d02f13cfe83d05f4a05)
  -u, --url TEXT        [required] (Example: https://mirrobits.lineageos.org/full/lineage-14.1-20170114-NIGHTLY-v500.zip)
  --help                Show this message and exit.
```

To remove use `FLASK_APP=app.py flask delrom [OPTIONS]`

```
Options:
  -f, --filename TEXT  [required]
  --help               Show this message and exit.
```


Example API Calls:
---
Obtaining rom list for a device:<br>
`GET /api/v1/<device>/<romtype>/<incremental>?after=<utc_timestamp>&version=<14.1>` (incremental can be anything, it is currently unused)<br>
`<device>` - Name of device. Example: `d2vzw`<br>
`<romtype>` - Type of rom. Example: `nightly`<br>
`<incremental>` - Caller device's incremental ID (ro.build.incr). Can be anything. <br>
`<after>` - Timestamp for current build on device. (optional) <br> 
`<romversion>` - Version of rom. Example: `14.1`(optional)<br>

Adding a build (requires an API key, see above) <br>
`POST /api/v1/add_build` <br>
```
{
  "device": "str",
  "filename": "str",
  "md5sum": "str",
  "romtype": "str",
  "url": "str",
  "version": "str"
}
```

To remove a build (requires an API key, see above) <br>
`POST /api/v1/del_build`
```
{
  "id": "str"
}

```

where "id" is a value returned by `/api/v1/<device>/<romtype>/<incremental>`.


TODO
====
- Lots I'm sure
