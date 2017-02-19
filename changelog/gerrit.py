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
from datetime import datetime
from flask.json import JSONEncoder

import json
import requests

class GerritJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, GerritUser):
                return {'id': obj.id, 'name': obj.name, 'username': obj.username, 'avatars': obj.avatars}
        except TypeError:
            pass
        return JSONEncoder.default(self, obj)

def parse_gerrit_datetime(d):
    if d is None:
        return None
    return datetime.strptime(d, "%Y-%m-%d %H:%M:%S.000000000")

def datetime_to_gerrit(d):
    return d.strftime('"%Y-%m-%d %H:%M:%S"')

class GerritThing(object):
    def __init__(self, url):
        self._url = url

    def _do_request(self, path, params):
        r = requests.get(self._url + path, params=params)
        text = r.text[5:]
        try:
            return json.loads(text)
        except Exception:
            print(text)
            return {}

class GerritUser(GerritThing):
    """Represents a user"""
    def __init__(self, url, obj):
        super(GerritUser, self).__init__(url)
        self.id = obj['_account_id']
        try:
            self.username = obj.get('username', obj['name'])
        except KeyError:
            self.username = 'unknown'
        try:
            self.name = obj.get('name', obj['username'])
        except KeyError:
            self.name = 'Anonymous Coward'
        try:
            self.email = obj['email']
        except KeyError:
            self.email = 'unknown'
        self.avatars = {}
        for i in obj['avatars']:
            self.avatars[i['height']] = i['url']

class GerritChange(GerritThing):
    """Represents a single change."""
    def __init__(self, url, obj):
        super(GerritChange, self).__init__(url)
        self._id = obj['id']
        self.project = obj['project']
        self.branch = obj['branch']
        self.change_id = obj['change_id']
        self.subject = obj['subject']
        self.status = obj['status']
        self.created = parse_gerrit_datetime(obj['created'])
        self.updated = parse_gerrit_datetime(obj['updated'])
        self.submitted = parse_gerrit_datetime(obj.get('submitted', None))
        self.number = obj['_number']
        self.url = self._url + '/' + str(self.number)
        self.owner = GerritUser(url, obj['owner'])
        self.labels = {}
        for lbl in obj['labels']:
            self.labels[lbl] = {}
            for k, v in obj['labels'][lbl].items():
                if k == 'value': continue
                self.labels[lbl][k] = GerritUser(url, v)

    def __str__(self):
        return 'GerritChange[status={},url={},project={},branch={},change_id={}]'.format(self.status, self._url, self.project,
                self.branch, self.change_id)

class GerritListing(GerritThing):
    """Represents a listing page on Gerrit (e.g. /changes/ or /projects/)"""
    def __init__(self, url, path, params, clazz, limit=-1):
        super(GerritListing, self).__init__(url)
        self.params = params
        self.path = path
        self._item_cache = []
        self._item_index = 0
        self._start = 0
        self._clazz = clazz
        self._limit = limit

    def _load_page(self):
        params = self.params
        params['S'] = self._start
        obj = self._do_request(self.path, params)
        appended = 0
        for el in obj:
            self._item_cache.append(self._clazz(self._url, el))
            appended += 1
        return appended


    def __iter__(self):
        return self

    def __next__(self):
        if self._limit != -1 and self._item_index > self._limit:
            raise StopIteration
        if self._item_index + 1 > len(self._item_cache):
            added = self._load_page()
            self._start += self.params['n']
            if added == 0:
                raise StopIteration
        self._item_index += 1
        return self._item_cache[self._item_index - 1]

    next = __next__

    def __str__(self):
        return 'GerritListing[path={},params={},clazz={},index={},cache_len={}]'.format(self.path, self.params,
                self._clazz, self._item_index, len(self._item_cache))

class GerritServer(GerritThing):
    """Represents a Gerrit server"""
    def __init__(self, url):
        super(GerritServer ,self).__init__(url)

    def changes(self, query='status:merged', n=50, limit=-1):
        # O is a bitmask in hex - see https://github.com/gerrit-review/gerrit/blob/master/gerrit-extension-api/src/main/java/com/google/gerrit/extensions/client/ListChangesOption.java
        params = { 'q': query, 'n': n, 'O': '81' }
        return GerritListing(self._url, '/changes/', params, GerritChange, limit)




