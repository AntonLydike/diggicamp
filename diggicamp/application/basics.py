from concurrent.futures import ThreadPoolExecutor

from ..scraper import Diggicamp
from ..config import DiggicampConf


def d_open(path: str = 'dgc.json'):
    conf = DiggicampConf.fromFile(path)
    return Diggicamp(conf)


def new(path: str = "dgc.json"):
    conf = DiggicampConf.default()
    conf.save(path)
    return Diggicamp(conf)


def save(dgc: Diggicamp, path: str = 'dgc.json'):
    dgc.conf.save(path)


def fetch(dgc: Diggicamp, threads: int = 16):
    dgc.get_courses(cached=False)

    if not dgc.conf.get('files'):
        return

    exec = ThreadPoolExecutor(max_workers=threads)
    # refresha all downloaded courses
    for course in dgc.conf.get('files'):
        exec.submit(dgc.get_files, course, cached=False)

    exec.shutdown()


def pull(dgc: Diggicamp, threads: int = 16):
    dgc.download_cached_folders(threads=threads)


def add_download(dgc: Diggicamp, folder_id: str, target: str, regex=None):
    """
    Add an entry to the list of folders we want to download
        folder_id: the id of the folder we want to download
        target: the target directory, where we want to download the folder
        regex (opt): a regex pattern which files need to match, in order to be downloaded
    """

    entry = {
        'folder': folder_id,
        'target': target
    }

    if regex:
        entry['regex'] = regex

    if not dgc.conf.get('downloads'):
        dgc.conf.set('downloads', [entry])
    else:
        dgc.conf.get('downloads').append(entry)
