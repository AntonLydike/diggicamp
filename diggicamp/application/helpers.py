from ..scraper import Diggicamp


def semester_by_name(dgc: Diggicamp, semester_name):
    for semester in dgc.conf.get('courses'):
        if semester['title'] == semester_name:
            return semester
    return None


def course_by_name(dgc: Diggicamp, course_name: str, semester_title=None, semester: dict = None):
    """
    find a course by it's name
        course_name: the name of the course (exact)
        semester_title (opt): the title of the semester which contains the specified xourse
        semester (opt): the semester object which contains the specified course

        if neither a semester_title or semester are specified, the newest semester is used
    """
    # ensure courses are loaded
    dgc.get_courses()

    if not semester:
        semester = dgc.conf.get('courses')[0]

        if semester_title:
            for entry in dgc.conf.get('courses'):
                if entry['title'] == semester_title:
                    semester = entry
                    break

    for course in semester['courses']:
        if course['name'] == course_name:
            return course

    return None


def folder_by_name(dgc: Diggicamp, folder_name: str, course):
    """find a folder by it's name
        folder_name: the name of the folder we are looking for (exact)
        course: can either be a course object, or a course id
    """
    if isinstance(course, dict):
        cid = course['id']
    else:
        cid = course

    folders = dgc.get_files_folders(cid)['folders']

    for folder in folders.values():
        if folder['name'] == folder_name:
            return folder

    return None


def course_by_id(dgc: Diggicamp, course_id: str):
    for semester in dgc.conf.get('courses'):
        for course in semester['courses']:
            if course['id'] == course_id:
                return course


def folder_by_id(dgc: Diggicamp, folder_id: str):
    return dgc.get_cached_folder(folder_id)
