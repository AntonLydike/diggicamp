import os
from concurrent.futures import ThreadPoolExecutor

from ..scraper import Diggicamp
from ..config import DiggicampConf
from .helpers import *


def d_open(path: str = 'dgc.json'):
    conf = DiggicampConf.fromFile(path)
    return Diggicamp(conf)


def new(path: str = "dgc.json"):
    if os.path.isfile(path):
        print("dgc is already initialized!")
        return None
    conf = DiggicampConf.default(url=None)
    conf.save(path)
    return Diggicamp(conf)


def save(dgc: Diggicamp, path: str = 'dgc.json'):
    dgc.conf.save(path)


def fetch(dgc: Diggicamp, threads: int = 32):
    dgc.get_courses(cached=False)

    if not dgc.conf.get('files'):
        return

    exec = ThreadPoolExecutor(max_workers=threads)
    # refresha all downloaded courses
    for course in dgc.conf.get('files'):
        exec.submit(dgc.get_files, course, cached=False)

    exec.shutdown()
    print("\nUpdated folders!")


def add_download(dgc: Diggicamp, folder_id: str, target: str, regex=None):
    """
    Add an entry to the list of folders/courses we want to download
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


def add_download_course(dgc: Diggicamp, course_id: str, target: str, regex=None):
    """
    Add an entry to the list of folders/courses we want to download
        course_id: the id of the course we want to download
        target: the target directory, where we want to download the folder
        regex (opt): a regex pattern which files need to match, in order to be downloaded
    """

    entry = {
        'course': course_id,
        'target': target
    }

    if regex:
        entry['regex'] = regex

    if not dgc.conf.get('downloads'):
        dgc.conf.set('downloads', [entry])
    else:
        dgc.conf.get('downloads').append(entry)


def pull(dgc: Diggicamp, threads: int = 32):
    if not dgc.conf.get('downloads'):
        print("No downloads configured")
        return

    downloads = dgc.conf.get('downloads')

    if threads < 1:
        raise Exception("downloading cannot happen with fewer than 1 threads!")

    exec = ThreadPoolExecutor(max_workers=threads)

    for rule in downloads:
        if 'folder' in rule:
            download_folder(dgc, rule, exec)
        elif 'course' in rule:
            download_course(dgc, rule, exec)
        else:
            print("  unknown download rule: " + rule)

    # wait for all threads to finish
    exec.shutdown()


def download_folder(dgc: Diggicamp, download_rule: dict, exec: ThreadPoolExecutor):
    """
    Execute a download rule, which uses a folder as source. This will download
    all files inside this folder
    """

    target = download_rule['target']
    fid = download_rule['folder']

    folder = dgc.get_cached_folder(fid)
    if not folder:
        print(f"""Folder {fid} (targeting {target}) is not in the cache!

Run
dgc show <course>
with the correct course to initially fetch the folder""")
        return

    if not os.path.exists(target):
        os.makedirs(target)

    for file in folder['files']:
        exec.submit(dgc._download_file, target, file)


def download_course(dgc: Diggicamp, download_rule: dict, exec: ThreadPoolExecutor):
    """
    Execute a download rule, which uses a course as source. This will download
    all folders in this course
    """

    folders = dgc.conf.get('files.' + download_rule['course'])

    if not folders:
        print("Course {} is not cached! Run\n\n    dgc show <course name>\n\n\
        to download the course details into the local cache!".format(download_rule['course']))

    for fid in folders:
        rule = download_rule.copy()
        rule['folder'] = fid
        rule['target'] += '/' + folders[fid]['name']
        download_folder(dgc, rule, exec)
