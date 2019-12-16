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


def fetch(dgc: Diggicamp):
    dgc.get_courses(cached=False)

    if not dgc.conf.get('files'):
        return
    # refresha all downloaded courses
    for course in dgc.conf.get('files'):

        dgc.get_files(course, cached=False)


def pull(dgc: Diggicamp):
    dgc.download_cached_folders()


def add_download(dgc: Diggicamp, folder_id: str, target: str, pattern=None):
    """
    Add/modify an entry to the list of folders we want to download
        folder_id: the id of the folder we want to download
        target: the target directory, where we want to download the folder
        pattern (opt): a regex pattern which files need to match, in order to be downloaded
    """
    if pattern:
        entry = {
            'target': target,
            'pattern': pattern
        }
    else:
        entry = target

    dgc.conf.set('downloads.' + folder_id, entry)
