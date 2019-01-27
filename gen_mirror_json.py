#!/usr/bin/env python
from __future__ import print_function
import hashlib
import json
import os
import sys
import zipfile

from datetime import datetime
from time import mktime, time

if len(sys.argv) < 2:
    print("usage python {} /path/to/mirror/base/url".format(sys.argv[0]))
    sys.exit()

FILE_BASE = sys.argv[1]
builds = {}

for f in [os.path.join(dp, f) for dp, dn, fn in os.walk(FILE_BASE) for f in fn]:
    data = open(f)
    filename = f.split('/')[-1]
    # lineage-14.1-20171129-nightly-hiaeul-signed.zip
    _, version, builddate, buildtype, device = os.path.splitext(filename)[0].split('-')
    print('hashing sha256 for {}'.format(filename), file=sys.stderr)
    sha256 = hashlib.sha256()
    for buf in iter(lambda : data.read(128 * 1024), b''):
        sha256.update(buf)
        try:
            with zipfile.ZipFile('{}{}'.format(BASE_PATH, filepath), 'r') as update_zip:
                build_prop = update_zip.read('system/build.prop').decode('utf-8')
                timestamp = int(re.findall('ro.build.date.utc=([0-9]+)', build_prop)[0])
        except:
            timestamp = int(mktime(datetime.strptime(builddate, '%Y%m%d').timetuple()))

    builds.setdefault(device, []).append({
        'sha256': sha256.hexdigest(),
        'size': os.path.getsize(f),
        'date': '{}-{}-{}'.format(builddate[0:4], builddate[4:6], builddate[6:8]),
        'datetime': timestamp,
        'filename': filename,
        'filepath': f.replace(FILE_BASE, ''),
        'version': version,
        'type': buildtype.lower()
    })
for device in builds.keys():
    builds[device] = sorted(builds[device], key=lambda x: x['date'])
print(json.dumps(builds, sort_keys=True, indent=4))
