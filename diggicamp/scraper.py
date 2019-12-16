import requests
import urllib

from .exceptions import WebException
from .pages import login, courses, course_files
from .config import DiggicampConf


class Diggicamp:
    def __init__(self, conf: DiggicampConf):
        self.session = requests.Session()
        self.conf = conf

    def login(self, user: str, pw: str):
        html = self._get('/?sso=webauth&cancel_login=1&again=yes')

        # parse page and get form data
        page = login.LoginPage(html)

        text = self._post(page.url(), data=page.assembleFormData(user, pw),
                          base='https://websso.uni-augsburg.de/')

        redirect = page.getRedirectUrlFromResponse(text)

        self._get(redirect, base='')

    def get_courses(self):
        page = courses.CoursesPage(self._get('/dispatch.php/my_courses'))

        courses_ = page.getCourses()

        self.conf.set('courses', courses_)

        return courses_

    def get_files(self, course_id: str):
        files = course_files.CourseFiles(self, course_id).getFileTree()

        self.conf.set('files.' + course_id, files)

        return files

    def _get(self, url: str, base=None):
        if base == None:
            base = self.conf.get('baseurl')
        resp = self.session.get(base + url)

        if resp.ok:
            print("GET " + url + " - OK")
            return resp.text
        else:
            raise WebException("Response is not valid!", base + url, resp)

    def _post(self, url: str, data, base=None):
        if base == None:
            base = self.conf.get('baseurl')
        resp = self.session.post(base + url, data=data)

        if resp.ok:
            print("POST " + url + " - OK")
            return resp.text
        else:
            print(resp.text)
            raise WebException("POST to " + url + " failed", resp)

    def _download(self, url: str, target: str, base=None):
        if base == None:
            base = self.conf.get('baseurl')
        resp = self.session.get(base + url)

        if resp.ok:
            print("GET [DOWNLOAD] " + url + " - OK")
            with open(target, "wb") as f:
                f.write(resp.content)
        else:
            raise WebException("GET " + base + url + " failed!", resp)

    def _download_file(self, target_dir: str, file: dict):
        id = file['id']
        name = urllib.parse.quote(file['fname'])
        return self._download(f'/sendfile.php?type=0&file_id={id}&file_name={name}', target_dir + '/' + file['fname'])
