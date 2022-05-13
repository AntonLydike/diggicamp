from ..scraper import Diggicamp
from ..config import DiggicampConf
from .helpers import folder_by_id, course_by_id


def print_courses(dgc: Diggicamp, all: bool = False, course=None):
    courses = dgc.get_courses()

    if not all:
        courses = courses[:1]

    if course:
        courses = [course]

    for semester in courses:
        print("{title}: ".format(**semester))

        for course in semester['courses']:
            print(" - {name}".format(**course))

        print("")


def print_folders(dgc: Diggicamp, course: dict):
    folders = dgc.get_files_folders(course['id'])['folders']

    print("{name}".format(**course))
    for folder in folders.values():
        print(" - {name}".format(**folder))
        for file in folder['files']:
            print("    * {fname}".format(**file))


def print_download_definitions(dgc: Diggicamp):
    dls: list = dgc.conf.get('downloads')

    if not dls:
        print("No downloads configured")
        return

    for dl in dls:
        index = dls.index(dl)

        if 'folder' in dl:
            name = folder_by_id(dgc, dl['folder'])['name']
        else:
            name = course_by_id(dgc, dl['course'])['name']
        print("[{:>2}] {:<40} → {}".format(index, name, dl['target']))
