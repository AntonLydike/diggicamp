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
        # output dictionary
        semesters = []
        # find the container of the seminar pages
        cont = self.dom.find('div', id='my_seminars')

        for semester in cont.find_all('table', class_='mycourses'):
            # remove the thead section, as it contains no valuable information
            semester.find('thead').extract()
            sem = {
                'title': unicode(semester.find('caption').string.strip()),
                'courses': []
            }

            for course in semester.find_all('tr'):
                link = course.find('a')
                sem['courses'].append({
                    'name': unicode(link.string.strip()),
                    'id': idFromUrl(link['href'])
                })

            semesters.append(sem)

        return semesters
