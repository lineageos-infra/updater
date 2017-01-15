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
* `wiki`: (*optional*) the name of the wiki page, exlcuding "\_Info". Defaults to the value of `model`.
For example, "i9300" would be shown on the website as a link to https://wiki.lineageos.org/w/i9300_Info.

Initial set up:
---
1. Install requirements with `pip install -r requirements.txt`
2. Copy `app.cfg.example` to `app.cfg`
3. Run with `FLASK_APP=app.py flask run`

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
  -a, --available TEXT             (Example: true)
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
