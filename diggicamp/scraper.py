import requests
from .exceptions import WebException
from .pages import login


class Diggicamp:
    baseurl = "https://digicampus.uni-augsburg.de/"

    def __init__(self):
        self.session = requests.Session()

    def login(self, user: str, pw: str):
        html = self._get(base='/?sso=webauth&cancel_login=1&again=yes',
                         url='https://digicampus.uni-augsburg.de')

        # parse page and get form data
        fdata = login.LoginPage(html).assembleFormData(user, pw)

    def _get(self, url: str, base=None):
        if not base:
            base = self.baseurl
        resp = self.session.get(base + url)

        if resp.ok:
            return resp.text
        else:
            raise WebException("Response is not valid!", base + url, resp)

    def _post(self, url: str, data, base=None):
        if not base:
            base = self.baseurl
        return self.session.post(base + url, data=data)
