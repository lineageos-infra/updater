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

import extensions


@extensions.cache.memoize()
def get_dependencies():
    # device_deps.json is generated using https://github.com/LineageOS/scripts/tree/main/device-deps-regenerator
    if os.path.isfile(Config.DEVICE_DEPS_PATH):
        with open(Config.DEVICE_DEPS_PATH) as f:
            return json.load(f)
    else:
        return requests.get(Config.OFFICIAL_DEVICE_DEPS_JSON_URL, timeout=60).json()


def get_dependencies_flat():
    return sorted({x for v in get_dependencies().values() for x in v})


def is_versions_branch(branch, versions=None):
    if not versions:
        return True

    for version in versions:
        if version in branch and '/' not in branch:
            return True

    return False


def get_project_repo(project):
    return project.split('/', 1)[1]


def get_device_dependencies(device):
    dependencies = get_dependencies()

    if device not in dependencies:
        return []

    return dependencies[device]


def get_type(project):
    # Matches https://github.com/LineageOS/android/blob/aa01966/snippets/lineage.xml#L163-L173
    type_overrides = {
        'infrastructure': [
            'LineageOS/charter',
            'LineageOS/cm_crowdin',
            'LineageOS/hudson',
            'LineageOS/mirror',
            'LineageOS/www',
            'LineageOS/lineage_wiki',
        ],
        'tools': [
            'LineageOS/contributors-cloud-generator',
            'LineageOS/scripts',
        ],
    }

    if type_override := next((x[0] for x in type_overrides.items() if project in x[1]), None):
        return type_override

    return 'device specific' if is_device_specific_repo(project) else 'platform'


def is_device_specific_repo(project):
    if '_kernel_' in project or '_device_' in project:
        return True

    repository = project.split("/", maxsplit=1)[1]
    return repository in get_dependencies_flat()


def is_related_change(device, project):
    if device == 'all':
        return True

    if 'android_' not in project:
        return False

    if is_device_specific_repo(project):
        if get_project_repo(project) in get_device_dependencies(device):
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
    if versions is None:
        versions = []

    query = ['status:merged']
    if before != -1:
        query.append('before:%s' % datetime_to_gerrit(datetime.fromtimestamp(before)))

    changes = [x for x in gerrit.changes(query=' '.join(query), n=100, limit=100)]
    last = 0

    for change in changes:
        last = get_timestamp(change.updated)

    return filter_changes(changes, device, versions), last


def get_paginated_changes(gerrit, page=0):
    return gerrit.changes(n=100, limit=100, page=page)
