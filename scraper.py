from diggicamp import Diggicamp, DiggicampConf


def open(path: str):
    conf = DiggicampConf.fromFile(path)
    return Diggicamp(conf)


def new(path: str):
    conf = DiggicampConf.default()
    conf.save(path)
    return Diggicamp(conf)


def fetch(dgc: Diggicamp):
    return None
