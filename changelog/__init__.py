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

from datetime import datetime

import json
import os
import requests

# device_deps.json is generated using https://github.com/LineageOS/scripts/tree/master/device-deps-regenerator
if os.path.isfile(Config.DEVICE_DEPS_PATH):
    with open(Config.DEVICE_DEPS_PATH) as f:
        dependencies = json.load(f)
else:
    dependencies = requests.get(Config.OFFICIAL_DEVICE_DEPS_JSON_URL).json()


def is_versions_branch(branch, versions=None):
    if not versions:
        return True

    for version in versions:
        if version in branch and '/' not in branch:
            return True

    return False


def get_project_repo(project):
    return project.split('/', 1)[1]


def is_device_specific_repo(project):
    return '_kernel_' in project or '_device_' in project


def is_related_change(device, project):
    if device == 'all':
        return True

    if 'android_' not in project:
        return False

    if is_device_specific_repo(project):
        if device not in dependencies:
            return False

        if get_project_repo(project) in dependencies[device]:
            return True

        return False

    return True


def get_timestamp(date):
    if not date:
        return None

    return int(date.timestamp())


def filter_changes(changes, device, versions):
    related_changes = []

    for change in changes:
        if not is_versions_branch(change.branch, versions):
            continue

        if not is_related_change(device, change.project):
            continue

        related_changes.append(change)

    return related_changes


def get_changes(gerrit, device=None, before=-1, versions=None):
    query = ['status:merged']
    if before != -1:
        query.append('before:%s' % datetime_to_gerrit(datetime.fromtimestamp(before)))

    changes = gerrit.changes(query=' '.join(query), n=100, limit=100)
    last = 0

    for change in changes:
        last = get_timestamp(change.updated)

    return filter_changes(changes, device, versions), last


def get_paginated_changes(gerrit, device, versions, page):
    changes = gerrit.changes(n=100, limit=100, page=page)
    return filter_changes(changes, device, versions)
