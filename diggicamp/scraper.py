import os
import urllib
import requests
from getpass import getpass

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
        if self.verbose:
            print("authed: {}".format(self.authed))

        html = self._get('/?sso=webauth&cancel_login=1&again=yes', unauthed=True)

        if not self.conf.has('credentials'):
            raise Exception("No credentials in config!")

        if self.conf.get('credentials.mode') == 'plain':
            user = self.conf.get('credentials.username')
            pw = self.conf.get('credentials.password')
        elif self.conf.get('credentials.mode') == 'prompt':
            user = self.conf.get('credentials.username')
            pw = getpass(prompt="Digicampus password: ")
            print("finishing login...")
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

        files = course_files.CourseFiles(self, course_id).getFileTree()

        self.conf.set('files.' + course_id, files)

        return files

    def get_cached_folder(self, fid: str):
        folders = self.conf.get('files')

        for course in folders.values():
            if course is not None and fid in course:
                return course[fid]

        return None

    def _get(self, url: str, base=None, unauthed: bool = False):
        if not unauthed and not self.authed:
            self.login()

        if base == None:
            base = self.conf.get('baseurl')
        
        resp = self.session.get(base + url)

        if resp.ok:
            if not unauthed and self.authed and is_not_logged_in(resp):
                if self.verbose:
                    print("lost auth in: {} with unauthed={}".format(url, unauthed))
                self._deauth()
                return self._get(url, base)
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
                self._deauth()
                if self.verbose:
                    print("lost auth in: {} with unauthed={}".format(url, unauthed))
                return self._post(url, data, base)

            return resp.text
        else:
            raise WebException("POST to " + url + " failed", resp)

    def _download(self, url: str, target: str, base=None):
        if not self.authed:
            self.login()

        if base == None:
            base = self.conf.get('baseurl')

        resp: requests.Response = self.session.get(base + url, stream=True)

        if self.verbose:
            print("Downloading " + base + url)

        if resp.ok:
            len_written = 0
            with open(target, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
                    len_written += len(chunk)
            
            if len_written == 0:
                os.remove(target)
                return False
            elif self.verbose:
                print("DOWNLOADED " + str(len_written) + " bytes into " + target)

            return True
        else:
            raise WebException("GET " + base + url + " failed!", resp)

    def _download_file(self, target_dir: str, file: dict):
        id = file['id']
        dl_type = file['type'] if 'type' in file else 0
        name = urllib.parse.quote(file['fname'])

        if (self.conf.get('downloaded_versions.' + id) == file['last_mod']):
            if self.verbose:
                print("{:<60} → {}".format(file['fname'], "cached"))
            return

        if self._download(f'/sendfile.php?type={dl_type}&file_id={id}&file_name={name}', target_dir + '/' + file['fname']):
            self.conf.set('downloaded_versions.' + id, file['last_mod'])
            print("{:<60} → {}".format(file['fname'], target_dir))
        else:
            print("{:<60} → failed".format(file['fname']))

    def _save_cookies(self):
        self.conf.set('cookies', self.session.cookies.get_dict())

    def _deauth(self):
        """
        remove old cookies, set authed to false, etc
        """
        self.session.cookies.clear()
        self.authed = False


def is_not_logged_in(resp: requests.Response) -> bool:
    # user is not logged in, if we get a html page back which contains the following text
    return resp.headers['Content-Type'] == 'text/html' and ('<button type="submit" class="accept button" name="Login">Anmelden</button>' in resp.text or '<form class="default" name="login"' in resp.text or '<!-- Startseite (nicht eingeloggt) -->' in resp.text)
