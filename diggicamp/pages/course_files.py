from bs4 import NavigableString
from .parsedpage import ParsedPage, unicode
import threading
import re
import requests


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

            folder = {
                'id': id,
                'name': unicode(" ".join(froot.find(id=f'folder_{id}_header').stripped_strings)),
                'files': []
            }
            folders[id] = folder

            # start a thread to download folder contents
            thread = threading.Thread(target=process_folder_async, args=(self.dgc, self.id, folder))
            thread.start()
            threads.append(thread)

        # wait for all threads to finish
        for thread in threads:
            thread.join()

        return folders


def process_folder_async(diggicamp, course: str, folder: dict):
    id = folder['id']
    html = diggicamp._post(f'/folder.php?cid={course}&data%5Bcmd%5D=tree&open={id}', data='')
    dom = ParsedPage(html).dom

    fcontainer = dom.find(id=f'folder_{id}', class_='folder_container')

    # TODO: parse subfolders recursively (maybe even with more threads?)
    # subfolders are contained inside this div: <div class="folder_container" id="folder_subfolders_ae1fd77a82bd4d1e74350e88ada5e58a"></div>

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

        if not 'href' in link:
            # if file is not downloadable, skip it
            continue

        fname = re.search(r'file_name=([^&]+)', link['href'])

        if not fname:
            raise Exception('link url has invalid format')

        fname = requests.utils.unquote(fname.group(1), encoding="1250")

        folder['files'].append({
            'id': id,
            'name': unicode(" ".join(file.find(id=f'file_{id}_header').stripped_strings)),
            'fname': fname
        })
