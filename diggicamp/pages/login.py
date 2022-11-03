from .parsedpage import ParsedPage, BeautifulSoup


class LoginPage(ParsedPage):
    def assembleFormData(self, usr: str, pw: str):
        # form data:
        fdata = {}
        # find form in page
        form = self.dom.find("form", attrs={'name': 'login'})
        # get all inputs inside the form
        for input in form.find_all("input"):
            if 'value' in input.attrs:
                fdata[input.attrs.get('name')] = input.attrs.get('value')

        fdata['username'] = usr
        fdata['password'] = pw

        return fdata

    def url(self):
        return self.dom.find("form", attrs={'name': 'login'}).attrs.get('action')

    def getRedirectUrlFromResponse(self, resp: str):
        dom = BeautifulSoup(resp, "html.parser")
        return dom.find('p', attrs={'class': 'info message'}).find('a').attrs.get('href')
