from .parsedpage import ParsedPage


class CoursesPage(ParsedPage):
    def getCourses(self):
        # output dictionary
        semesters = {}
        # find the container of the seminar pages
        cont = self.dom.find('div', id='my_seminars')

        for semester in cont.find_all('table', class_='mycourses'):
            # remove the thead section, as it contains no valuable information
            semester.find('thead').extract()
            sem = {
                'title': semester.find('caption').string.strip(),
                'courses': []
            }

            for course in semester.find_all('tr'):
                link = course.find('a')
                sem['courses'].append({
                    'name': link.string.strip(),
                    'url': link['href']
                })

            semesters[sem['title']] = sem

        return semesters
