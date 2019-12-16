import json


class DiggicampConf:
    def __init__(self, settings: object):
        self.opts = settings

    def get(self, key: str) -> str:
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

    def save(self, file: str):
        with open(file, "w") as f:
            f.write(json.dumps(self.opts, indent=2))

    @staticmethod
    def fromFile(fname: str) -> 'DiggicampConf':
        with open(fname, "r") as f:
            return DiggicampConf(json.load(f))

    @staticmethod
    def fromString(string: str) -> DiggicampConf:
        return DiggicampConf(json.loads(string))

    @staticmethod
    def default() -> DiggicampConf:
        conf = DiggicampConf({})
        conf.set('baseurl', 'https://digicampus.uni-augsburg.de/')
