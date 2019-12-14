import json


class DiggicampConf:
    def __init__(self, settings: object):
        self.opts = settings

    def get(self, key: str):
        obj = self.opts
        for path in key.split("."):
            if path in obj:
                obj = obj[path]
            else:
                return None

    def set(self, key: str, val: any):
        keys = key.split(".")
        lastKey = keys[len(keys)-1]
        obj = self.opts
        for path in keys[:len(keys)-1]:
            if not path in obj:
                obj[path] = {}
            obj = obj[path]
        obj[lastKey] = val

    @staticmethod
    def fromFile(fname: str):
        with open(fname, "r") as f:
            return DiggicampConf(json.load(f))

    @staticmethod
    def fromString(string: str):
        return DiggicampConf(json.loads(string))
