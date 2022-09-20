import json
import re
from .parsedpage import ParsedPage, unicode


def idFromUrl(url: str):
    match = re.search(r'auswahl=([^&]+)', url)
    if match:
        return match.group(1)
    else:
        return None


class CoursesPage(ParsedPage):
    def getCourses(self):
        # extract the json data from the html
        courses_json = re.search(r"window.STUDIP.MyCoursesData\s*=\s*([^\n]*})", str(self.dom)).group(1)
        courses_data = json.loads(courses_json)

        return [{'title': group['name'], 'courses': [
            {'name': course['name'], 'id': course['id']} for course in courses_data['courses'].values() if course['id'] in group['data'][0]['ids']
        ]} for group in courses_data['groups']]
