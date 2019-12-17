import requests
import urllib
import os

from .exceptions import WebException, NotLoggedInScepion
from .pages import login, courses, course_files
from .config import DiggicampConf


class Diggicamp:
    authed = False
    verbose = False

    def __init__(self, conf: DiggicampConf, verbose: bool = False):
        self.session = requests.Session()
        self.conf = conf
        self.verbose = verbose

        if conf.has('cookies'):
            self.authed = True
            requests.utils.add_dict_to_cookiejar(self.session.cookies, conf.get('cookies'))

    def login(self):
        print("logging in...")
        html = self._get('/?sso=webauth&cancel_login=1&again=yes', unauthed=True)

        if not self.conf.has('credentials'):
            raise Exception("No credentials in config!")

        if self.conf.get('credentials.mode') == 'plain':
            user = self.conf.get('credentials.username')
            pw = self.conf.get('credentials.password')
        else:
            raise Exception("Unknown auth mode: " + self.conf.get('credentials.mode'))

        # parse page and get form data
        page = login.LoginPage(html)

        text = self._post(page.url(), data=page.assembleFormData(user, pw),
                          base='https://websso.uni-augsburg.de/', unauthed=True)

        redirect = page.getRedirectUrlFromResponse(text)

        self._get(redirect, base='', unauthed=True)

        self.authed = True
        self._save_cookies()

    def get_courses(self, cached: bool = True):
        if cached and self.conf.has('courses'):
            return self.conf.get('courses')

        print("getting course list from server...")
        page = courses.CoursesPage(self._get('/dispatch.php/my_courses'))

        courses_ = page.getCourses()

        self.conf.set('courses', courses_)

        return courses_

    def get_files(self, course_id: str, cached: bool = True):
        if cached and self.conf.has('files.' + course_id):
            return self.conf.get('files.' + course_id)

        print("searching server for folder contents...")
        files = course_files.CourseFiles(self, course_id).getFileTree()

        self.conf.set('files.' + course_id, files)

        return files

    def get_cached_folder(self, fid: str):
        folders = self.conf.get('files')

        for course in folders.values():
            for folder in course.values():
                if folder['id'] == fid:
                    return folder

        return None

    def download_cached_folders(self):
        if not self.conf.get('downloads'):
            print("No downloads configured")
            return

        downloads = self.conf.get('downloads')

        for fid in downloads:
            directive = downloads[fid]
            target = directive if isinstance(directive, str) else directive['target']

            folder = self.get_cached_folder(fid)
            if not folder:
                print(f"Folder {fid} (targeting {target}) is not in the cache!")
                continue

            if not os.path.exists(target):
                os.makedirs(target)

            for file in folder['files']:
                self._download_file(target, file)

    def _get(self, url: str, base=None, unauthed: bool = False):
        if not unauthed and not self.authed:
            self.login()

        if base == None:
            base = self.conf.get('baseurl')

        resp = self.session.get(base + url)

        if resp.ok:
            if not unauthed and self.authed and is_not_logged_in(resp):
                self.authed = False
                return self._get(url, base)

            if self.verbose:
                print("GET " + url + " - OK")

            return resp.text
        else:
            raise WebException("Response is not valid!", base + url, resp)

    def _post(self, url: str, data, base=None, unauthed: bool = False):
        if not unauthed and not self.authed:
            self.login()

        if base == None:
            base = self.conf.get('baseurl')

        resp = self.session.post(base + url, data=data)

        if resp.ok:
            if not unauthed and self.authed and is_not_logged_in(resp):
                self.authed = False
                return self._post(url, data, base)

            if self.verbose:
                print("POST " + url + " - OK")

            return resp.text
        else:
            print(resp.text)
            raise WebException("POST to " + url + " failed", resp)

    def _download(self, url: str, target: str, base=None):
        if not self.authed:
            self.login()

        if base == None:
            base = self.conf.get('baseurl')

        resp: requests.Response = self.session.get(base + url)

        if resp.ok:
            if self.authed and is_not_logged_in(resp):
                self.authed = False
                return self._download(url, target, base)

            if self.verbose:
                print("GET [DOWNLOAD] " + url + " - OK")

            with open(target, "wb") as f:
                f.write(resp.content)
        else:
            raise WebException("GET " + base + url + " failed!", resp)

    def _download_file(self, target_dir: str, file: dict):
        print("{:<60} → {}".format(file['fname'], target_dir))
        id = file['id']
        name = urllib.parse.quote(file['fname'])
        return self._download(f'/sendfile.php?type=0&file_id={id}&file_name={name}', target_dir + '/' + file['fname'])

    def _save_cookies(self):
        self.conf.set('cookies', self.session.cookies.get_dict())


def is_not_logged_in(resp: requests.Response) -> bool:
    # user is not logged in, if we get a html page back which contains the following text
    return resp.headers['Content-Type'] == 'text/html' and '<!-- Startseite (nicht eingeloggt) -->' in resp.text
