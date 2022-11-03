import json
import os
import re
import threading
from datetime import datetime

from .helpers import clean_name_for_fs
from .parsedpage import ParsedPage


class CourseFiles:
    def __init__(self, diggicamp, courseId: str):
        self.id = courseId
        self.dgc = diggicamp

    def getFileTree(self) -> dict:
        # root files
        root_files = []
        # list of threads
        threads = []

        try:
            html = self.dgc._get(f'/dispatch.php/course/files?cid={self.id}&cmd=tree')
        except:
            return {}

        dom = ParsedPage(html).dom

        # handle FOLDERS:
        # initialize an asynchronous callback collection
        # everyone can call add_to_bag to add a return value to the collection
        (get_folder_bag, add_to_folder_bag) = create_bag()
        sub_folders = get_folders(dom)
        if sub_folders is not None:
            for folder in sub_folders:
                # start a thread to download folder contents
                thread = threading.Thread(target=process_folder_async, args=(self.dgc, self.id, folder['id'], folder['name'], add_to_folder_bag))
                thread.start()
                threads.append(thread)

        # handle FILES in root directory
        process_files(dom, root_files)

        # wait for all threads to finish
        for thread in threads:
            thread.join()

        result = {
            'root_files': root_files,
            'folders': get_folder_bag()
        }

        return result


# returns all folders ((id, name) tuple) in the specified dom
def get_folders(dom: str):
    folders_json = re.search(r"data-folders='([^']*)'", str(dom))
    folders_data = json.loads(folders_json.group(1)) if folders_json else []
    return [{
        'id': folder['id'],
        'name': clean_name_for_fs(folder['name'])
    } for folder in folders_data]


def process_files(dom: str, output):
    files_json = re.search(r"data-files='([^']*)'", str(dom))
    files_data = json.loads(files_json.group(1)) if files_json else []

    for file in files_data:
        if not file['download_url']:
            continue
        name = clean_name_for_fs(file['name'])
        output.append({
            'id': file['id'],
            'name': name,
            'fname': name,
            'type': 0,
            'last_mod': str(datetime.fromtimestamp(file['chdate'] or datetime.now().timestamp()))
        })
        print('.', end='', flush=True)


def process_folder_async(diggicamp, course: str, id: str, name: str, add_folder):
    # print a little progress indicator
    print('.', end='', flush=True)

    html = diggicamp._post(f'/dispatch.php/course/files/index/{id}?cid={course}', data=f'getfolderbody={id}')
    dom = ParsedPage(html).dom

    folder = {
        'id': id,
        'name': name,
        'files': []
    }

    # query subfolders
    subfolders = get_folders(dom)
    if subfolders:
        for subfolder in subfolders:
            process_folder_async(diggicamp, course, subfolder['id'], os.path.join(name, subfolder['name']), add_folder)

    process_files(dom, folder['files'])

    add_folder(folder)


# async folder collection
# call add_to_bag to add a value
# call get_bag to get all current contents
def create_bag():
    bag = []

    def get_bag():
        return bag

    def add_to_bag(item):
        bag.append(item)

    return (get_bag, add_to_bag)
