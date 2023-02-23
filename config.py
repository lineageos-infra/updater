import os


class Config(object):
    GERRIT_URL = os.environ.get('GERRIT_URL', 'https://review.lineageos.org')
    WIKI_INSTALL_URL = os.environ.get('WIKI_INSTALL_URL', 'https://wiki.lineageos.org/devices/{device}/install')
    WIKI_INFO_URL = os.environ.get('WIKI_INFO_URL', 'https://wiki.lineageos.org/devices/{device}')
    STATUS_URL = os.environ.get('STATUS_URL', '#')

    UPSTREAM_URL = os.environ.get('UPSTREAM_URL', '')
    DOWNLOAD_BASE_URL = os.environ.get('DOWNLOAD_BASE_URL', 'https://mirrorbits.lineageos.org')
    EXTRAS_BLOB = os.environ.get('EXTRAS_BLOB', 'extras.json')

    DEVICES_JSON_PATH = os.environ.get('DEVICES_JSON_PATH', 'devices.json')
    DEVICES_LOCAL_JSON_PATH = os.environ.get('DEVICES_LOCAL_JSON_PATH', 'devices_local.json')
    OFFICIAL_DEVICES_JSON_URL = os.environ.get('OFFICIAL_DEVICES_JSON_URL', 'https://raw.githubusercontent.com/LineageOS/hudson/master/updater/devices.json')
    DEVICE_DEPS_PATH = os.environ.get('DEVICE_DEPS_PATH', 'device_deps.json')
    OFFICIAL_DEVICE_DEPS_JSON_URL = os.environ.get('OFFICIAL_DEVICE_DEPS_JSON_URL', 'https://raw.githubusercontent.com/LineageOS/hudson/master/updater/device_deps.json')


class FlaskConfig(object):
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '3600'))
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_REDIS_HOST = os.environ.get('CACHE_REDIS_HOST', 'redis')
    CACHE_REDIS_DB = os.environ.get('CACHE_REDIS_DB', 4)
    CACHE_REDIS_PASSWORD = os.environ.get("CACHE_REDIS_PASSWORD", None)
