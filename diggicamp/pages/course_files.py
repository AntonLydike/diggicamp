from bs4 import NavigableString
from .parsedpage import ParsedPage, unicode
from datetime import datetime
import threading
import requests
import re


class CourseFiles:
    def __init__(self, diggicamp, courseId: str):
        self.id = courseId
        self.dgc = diggicamp

    def getFileTree(self):
        # folder dict
        folders = {}
        # list of threads
        threads = []

        dom = ParsedPage(self.dgc._get(f'folder.php?cid={self.id}&cmd=tree')).dom

        root = dom.find('div', id='folder_subfolders_root')

        # initialize a asynchronous callback collection
        # everyone can call add_to_bag to add a return value to the collection
        (get_bag, add_to_bag) = create_bag()

        for froot in root.children:
            # what we want to know about this folder
            id = None
            if froot.div:
                id = froot.div.string.strip()
            else:
                elem = froot.find(id=re.compile(r'folder_[A-f0-9]{32}_body'))
                if elem:
                    match = re.search(r'folder_([A-f0-9]{32})_body', elem['id'])
                    if not match:
                        raise Exception("id matches, but then does not match?!", elem.prettify())
                    id = match.group(1)
                else:
                    print("no folder id discovered!\n" + froot.prettify())
                    continue

            name = unicode(" ".join(froot.find(id=f'folder_{id}_header').stripped_strings))

            # start a thread to download folder contents
            thread = threading.Thread(target=process_folder_async, args=(self.dgc, self.id, id, name, add_to_bag))
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


def process_folder_async(diggicamp, course: str, id: str, name: str, add_folder):
    # print a little progress indicator
    print('.', end='', flush=True)

    html = diggicamp._post(f'/folder.php?cid={course}&data%5Bcmd%5D=tree&open={id}', data=f'getfolderbody={id}')
    dom = ParsedPage(html).dom

    folder = {
        'id': id,
        'name': name,
        'files': []
    }

    fcontainer = dom.find(id=f'folder_{id}', class_='folder_container')

    # query subfolders
    subfolders = dom.find(id=f'folder_subfolders_{id}', class_='folder_container')
    #print("found " + str(len(subfolders.find_all('div', recoursive=False))))
    if subfolders:
        for subfolder in subfolders.findChildren('div', recoursive=False):
            idfield = subfolder.find(id=re.compile('^getmd5'))
            if not idfield:
                continue  # this happens quite often and is not a sign of failure on our side, rather digicampus being derpy
            subid = unicode(" ".join(idfield.stripped_strings))
            subname = unicode(" ".join(subfolder.find(id=f'folder_{subid}_header').stripped_strings))
            process_folder_async(diggicamp, course, subid, subname, add_folder)

    if not fcontainer:
        return

    for file in list(fcontainer.children):
        if isinstance(file, NavigableString):
            continue

        if file.div:
            id = file.div.string.strip()
        else:
            raise Exception("No id for file found!", file.prettify())

        link = file.find(id=f'file_{id}_header').parent.previous_sibling

        if not link:
            raise Exception("link not found!")

        if not 'href' in link.attrs:
            # if file is not downloadable, skip it
            continue

        fname = re.search(r'file_name=([^&]+)', link['href'])

        if not fname:
            raise Exception('link url has invalid format')

        fname = requests.utils.unquote(fname.group(1), encoding="1250")

        last_modified_elm = file.find('td', class_='printhead', align='right')
        if last_modified_elm:
            last_modified_elm.a.extract()
            last_modified = last_modified_elm.string.strip()
        else:
            last_modified = str(datetime.now())

        folder['files'].append({
            'id': id,
            'name': unicode(" ".join(file.find(id=f'file_{id}_header').stripped_strings)),
            'fname': fname,
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
