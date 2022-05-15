import json
from typing import Any

import diggicamp

CONFIG_VERSION = "1.3.0"


class DiggicampConf:

    def __init__(self, settings: object):
        self.opts = settings

        if 'version' not in settings or settings['version'] != CONFIG_VERSION:
            print("Different version detected")
            diggicamp.migrate_config(self)

    def get(self, key: str) -> Any:
        obj = self.opts
        for path in key.split("."):
            if path in obj:
                obj = obj[path]
            else:
                return None
        return obj

    def set(self, key: str, val: any):
        keys = key.split(".")
        lastKey = keys[len(keys) - 1]
        obj = self.opts
        for path in keys[:len(keys) - 1]:
            if path not in obj:
                obj[path] = {}
            obj = obj[path]
        obj[lastKey] = val

    def save(self, file: str):
        with open(file, "w") as f:
            f.write(json.dumps(self.opts, indent=2, default=lambda o: '<not serializable>'))

    def has(self, key: str):
        obj = self.opts
        for path in key.split("."):
            if path in obj:
                obj = obj[path]
            else:
                return False
        return True

    def add_auth(self, mode, **args):
        args['mode'] = mode
        self.set('credentials', args)

    def version(self):
        return self.get('version')

    def cleanup(self):
        delkeys = ['course_download', 'downloads', 'downloaded_versions']
        for key in delkeys:
            self.delkey(key)

    def delkey(self, key):
        if self.has(key):
            # get path to parent
            parent = '.'.join(key.split('.')[0:-1])
            if not parent:
                obj = self.opts
            else:
                obj = self.get(parent)
            # remove object from dict
            del obj[key.split('.')[-1]]

    @staticmethod
    def fromFile(fname: str) -> 'DiggicampConf':
        with open(fname, "r") as f:
            return DiggicampConf(json.load(f))

    @staticmethod
    def fromString(string: str) -> 'DiggicampConf':
        return DiggicampConf(json.loads(string))

    @staticmethod
    def default(url: str) -> 'DiggicampConf':
        conf = DiggicampConf({'version': CONFIG_VERSION})
        if url[-1] != "/":
            url = url + "/"

        conf.set('baseurl', url)
        return conf
