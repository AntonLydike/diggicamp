from bs4 import NavigableString
from .parsedpage import ParsedPage, unicode
from datetime import datetime
import threading
import requests
import re
import os

class CourseFiles:
    def __init__(self, diggicamp, courseId: str):
        self.id = courseId
        self.dgc = diggicamp

    def getFileTree(self):
        # folder dict
        folders = {}
        # list of threads
        threads = []

        dom = ParsedPage(self.dgc._get(f'/dispatch.php/course/files?cid={self.id}&cmd=tree')).dom

        # initialize a asynchronous callback collection
        # everyone can call add_to_bag to add a return value to the collection
        (get_bag, add_to_bag) = create_bag()
        sub_folders = get_folders(dom)
        if not sub_folders:
            return
        for folder in sub_folders:
            # start a thread to download folder contents            
            thread = threading.Thread(target=process_folder_async, args=(self.dgc, self.id, folder['id'], folder['name'], add_to_bag))
            thread.start()
            threads.append(thread)

        # wait for all threads to finish
        for thread in threads:
            thread.join()

        count = 0
        for folder in get_bag():
            folders[folder['id']] = folder
            count += 1

        return folders

#returns all folders ((id, name) tuple) in the specified dom
def get_folders(dom: str):
    subfolders = dom.find('tbody', class_='subfolders').find_all(id=re.compile(r'row_folder_[A-f0-9]{32}'))
    output_folders = []
    for folder in subfolders:
        id = folder['id'][11:]
        name = folder.find_all('a')[1].text.strip()
        #these characters are forbidden in directory names. thx windows...
        name = name.translate(str.maketrans({"/":  "", "<":  "", ">": "", ":":  "", "\"":  "", "\\":  "", "?":  "", "*":  "", "|":  ""}))
        output_folders.append({
            'id': id,
            'name': name,
        })
    return output_folders


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

    fcontainer = dom.find('tbody', class_='files').find_all(id=re.compile(r'fileref_[A-f0-9]{32}'))

    if not fcontainer:
        return

    for file in fcontainer:
        if isinstance(file, NavigableString):
            continue

        if file:
            id = file['id'][8:]
        else:
            raise Exception("No id for file found!", file.prettify())

        link = file.find_all('td')[2].find('a')

        if not link:
            raise Exception("link not found!")

        if not 'href' in link.attrs:
            # if file is not downloadable, skip it
            continue
        
        fname = link.text.strip()
        if not fname:
            raise Exception("Filename not found!")
        
        last_modified_elm = file.find_all('td')[5]['title']
        if last_modified_elm:
            last_modified = last_modified_elm.strip()
        else:
            last_modified = str(datetime.now())

        folder['files'].append({
            'id': id,
            'name': fname,
            'fname': fname,
            'type': 0,
            'last_mod': last_modified
        })
        print('.', end='', flush=True)

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
