import requests
from .exceptions import WebException
from .pages import login, courses
from .config import DiggicampConf


class Diggicamp:
    baseurl = "https://digicampus.uni-augsburg.de/"

    def __init__(self):
        self.session = requests.Session()

    def login(self, user: str, pw: str):
        html = self._get('/?sso=webauth&cancel_login=1&again=yes')

        # parse page and get form data
        page = login.LoginPage(html)

        text = self._post(page.url(), data=page.assembleFormData(user, pw),
                          base='https://websso.uni-augsburg.de/')

        redirect = page.getRedirectUrlFromResponse(text)

        self._get(redirect, base='')

    def get_courses(self):
        html = self._get('/dispatch.php/my_courses')

        page = courses.CoursesPage(html)

        return page.getCourses()

    def _get(self, url: str, base=None):
        if base == None:
            base = self.baseurl
        resp = self.session.get(base + url)

        if resp.ok:
            print("GET " + url + " - OK")
            return resp.text
        else:
            raise WebException("Response is not valid!", base + url, resp)

    def _post(self, url: str, data, base=None):
        if base == None:
            base = self.baseurl
        resp = self.session.post(base + url, data=data)

        if resp.ok:
            print("POST " + url + " - OK")
            return resp.text
        else:
            print(resp.text)
            raise WebException("POST to " + url + " failed", resp)

    def _download(self, url: str, target: str, base=None):
        if base == None:
            base = self.baseurl
        resp = self.session.get(base + url)

        if resp.ok:
            print("GET [DOWNLOAD] " + url + " - OK")
            with open(target, "wb") as f:
                f.write(resp.content)
        else:
            raise WebException("GET " + base + url + " failed!", resp)
