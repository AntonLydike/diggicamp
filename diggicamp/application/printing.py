from ..scraper import Diggicamp
from ..config import DiggicampConf


def print_courses(dgc: Diggicamp, all: bool = False):
    courses = dgc.get_courses()

    if not all:
        courses = courses[:1]

    for semester in courses:
        print("{title}: ".format(**semester))

        for course in semester['courses']:
            print(" - {name}".format(**course))

        print("")


def print_folders(dgc: Diggicamp, course: dict):
    folders = dgc.get_files(course['id'])

    print("{name}".format(**course))
    for folder in folders.values():
        print(" - {name}".format(**folder))
        for file in folder['files']:
            print("    * {fname}".format(**file))
