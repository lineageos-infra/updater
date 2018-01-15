#!/usr/bin/env python
from __future__ import print_function
import hashlib
import json
import os
import sys

if len(sys.argv) < 2:
    print("usage python {} /path/to/mirror/base/url".format(sys.argv[0]))
    sys.exit()

FILE_BASE = sys.argv[1]
builds = {}

for f in [os.path.join(dp, f) for dp, dn, fn in os.walk(FILE_BASE) for f in fn]:
    data = open(f).read()
    filename = f.split('/')[-1]
    # lineage-14.1-20171129-nightly-hiaeul-signed.zip
    _, version, builddate, buildtype, device = os.path.splitext(filename)[0].split('-')
    print('hashing sha256 for {}'.format(filename), file=sys.stderr)
    sha256 = hashlib.sha256(data).hexdigest()
    builds.setdefault(device, []).append({
        'sha256': hashlib.sha256(data).hexdigest(),
        'size': os.path.getsize(f),
        'date': '{}-{}-{}'.format(builddate[0:4], builddate[4:6], builddate[6:8]),
        'filename': filename,
        'filepath': f.replace(FILE_BASE, ''),
        'version': version,
        'type': buildtype.lower()
    })
for device in builds.keys():
    builds[device] = sorted(builds[device], key=lambda x: x['date'])
print(json.dumps(builds, sort_keys=True, indent=4))
