import os
from concurrent.futures import ThreadPoolExecutor
from typing import Literal

from ..scraper import Diggicamp
from ..config import DiggicampConf
from .helpers import *


def d_open(path: str = 'dgc.json'):
    conf = DiggicampConf.fromFile(path)
    return Diggicamp(conf)


def new(url: str, path: str = "dgc.json"):
    if os.path.isfile(path):
        print("Dgc is already initialized!")
        return None
    conf = DiggicampConf.default(url)
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


def add_download(dgc: Diggicamp, download_id: str, target: str, regex=None,
                 download_type: Literal['folder', 'course'] = 'folder'):
    """
    Add an entry to the list of folders/courses we want to download
        download_id: the id of the folder/course we want to download
        target: the target directory, where we want to download the folder/course
        regex (opt): a regex pattern which files need to match, in order to be downloaded
    """

    entry = {
        download_type: download_id,
        'target': target
    }

    if regex:
        entry['regex'] = regex

    if not dgc.conf.get('downloads'):
        dgc.conf.set('downloads', [entry])
    elif not any(download_entry[download_type] == download_id for download_entry in dgc.conf.get('downloads')):
        dgc.conf.get('downloads').append(entry)
    else:
        print('Download was already added.')


def pull(dgc: Diggicamp, threads: int = 32):
    if not dgc.conf.get('downloads'):
        print("No downloads configured")
        return

    downloads = dgc.conf.get('downloads')

    if threads < 1:
        raise Exception("Downloading cannot happen with fewer than 1 threads!")

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
        course = course_by_id(dgc, download_rule['course'])
        folders = dgc.get_files(course['id'])

    for fid in folders:
        rule = download_rule.copy()
        rule['folder'] = fid
        rule['target'] += '/' + folders[fid]['name']
        download_folder(dgc, rule, exec)


def clean_config(dgc: Diggicamp):
    dgc.conf.cleanup()
