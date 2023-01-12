#
# Copyright (C) 2017 The LineageOS Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from __future__ import absolute_import
from changelog.gerrit import GerritServer, datetime_to_gerrit
from config import Config
from requests.exceptions import ConnectionError

from datetime import datetime, timedelta

import json
import os
import requests

# device_deps.json is generated using https://github.com/LineageOS/scripts/tree/master/device-deps-regenerator
if os.path.isfile(Config.DEVICE_DEPS_PATH):
    with open(Config.DEVICE_DEPS_PATH) as f:
        dependencies = json.load(f)
else:
    dependencies = requests.get("https://raw.githubusercontent.com/LineageOS/hudson/master/updater/device_deps.json").json()

is_qcom = {}

def is_related_change(gerrit, device, curbranch, project, branch):
    if not ('/android_' in project or '-kernel-' in project):
        return False

    if curbranch:
        major = curbranch.split('.')[0]

        if int(major) >= 20:
            # branch = "lineage-20" or "lineage-20.0" or "lineage-20.0-.*"
            if not any(branch == x or branch.startswith(f'{x}-') for x in [f'lineage-{major}', f'lineage-{curbranch}']):
                return False
        else:
            # branch = "cm-14.1-caf-msm8996" or "cm-14.1" or "stable/cm-13.0-ZNH5Y"
            if curbranch not in branch or "/" in branch:
                return False

    if device not in dependencies:
        return True

    deps = dependencies[device]
    if project.split('/', 1)[1] in deps:
        # device explicitly depends on it
        return True

    if '_kernel_' in project or '_device_' in project or 'samsung' in project or 'nvidia' in project \
            or '_omap' in project or 'FlipFlap' in project or 'lge-kernel-mako' in project:
        return False

    if not ('hardware_qcom_' in project or project.endswith('-caf')):
        # not a qcom-specific HAL
        return True

    # probably a qcom-only HAL
    qcom = True
    if device in is_qcom:
        qcom = is_qcom[device]
    else:
        for dep in deps:
            # Exynos devices either depend on hardware/samsung_slsi* or kernel/samsung/smdk4412
            if 'samsung_slsi' in dep or 'smdk4412' in dep:
                qcom = False
                break
            # Tegras use hardware/nvidia/power
            elif '_nvidia_' in dep:
                qcom = False
                break
            # Omaps use hardware/ti/omap*
            elif '_omap' in dep:
                qcom = False
            # Mediateks use device/cyanogen/mt6xxx-common or kernel/mediatek/*
            elif '_mt6' in dep or '_mediatek_' in dep:
                qcom = False

        is_qcom[device] = qcom

    return qcom

def get_timestamp(ts):
    if not ts:
        return None
    return int((ts - datetime(1970, 1, 1)).total_seconds())

def get_changes(gerrit, device=None, before=-1, version='14.1', status_url='#'):
    last_release = -1

    query = 'status:merged'
    if last_release != -1:
        query += ' after:' + datetime_to_gerrit(last_release)
    if before != -1:
        query += ' before:' + datetime_to_gerrit(datetime.fromtimestamp(before))

    changes = gerrit.changes(query=query, n=100, limit=100)

    nightly_changes = []
    last = 0
    try:
        for c in changes:
            last = get_timestamp(c.updated)
            if is_related_change(gerrit, device, version, c.project, c.branch):
                nightly_changes.append({
                    'project': c.project,
                    'subject': c.subject,
                    'submitted': get_timestamp(c.submitted),
                    'updated': get_timestamp(c.updated),
                    'url': c.url,
                    'owner': c.owner,
                    'labels': c.labels
                })
    except ConnectionError as e:
        nightly_changes.append({
            'project': None,
            'subject': None,
            'submitted': 0,
            'updated': 0,
            'url': status_url,
            'owner': None,
            'labels': None
            })
    return {'last': last, 'res': nightly_changes }
