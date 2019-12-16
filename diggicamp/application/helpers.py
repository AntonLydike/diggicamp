from ..scraper import Diggicamp


def course_by_name(dgc: Diggicamp, course_name: str, semester_title=None, semester=None):
    """
    find a course by it's name
        course_name: the name of the course (exact)
        semester_title (opt): the title of the semester which contains the specified xourse
        semester (opt): the semester object which contains the specified xourse

        if neither a semester_title or semester are specified, the newest semester is used
    """
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

    folders = dgc.get_files(cid)

    for folder in folders.values():
        if folder['name'] == folder_name:
            return folder

    return None
