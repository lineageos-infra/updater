#!/usr/bin/env python3
from __future__ import print_function
import hashlib
import json
import os
import re
import sys
import zipfile

from datetime import datetime
from time import mktime

if len(sys.argv) < 2:
    print("usage python3 {} /path/to/mirror/base/url".format(sys.argv[0]))
    sys.exit()

FILE_BASE = sys.argv[1]
builds = {}

for f in [os.path.join(dp, f) for dp, dn, fn in os.walk(FILE_BASE) for f in fn]:
    data = open(f, 'rb')
    filename = f.split('/')[-1]
    # lineage-14.1-20171129-nightly-hiaeul-signed.zip
    _, version, builddate, buildtype, device = os.path.splitext(filename)[0].split('-')
    print('hashing sha256 for {}'.format(filename), file=sys.stderr)
    sha256 = hashlib.sha256()
    for buf in iter(lambda: data.read(128 * 1024), b''):
        sha256.update(buf)

        try:
            with zipfile.ZipFile(f'{FILE_BASE}/{filename}', 'r') as update_zip:
                build_prop = update_zip.read('META-INF/com/android/metadata').decode('utf-8')
                timestamp = (re.findall('post-timestamp=([0-9]+)', build_prop)[0])
        except Exception as e:
            print(e)
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
