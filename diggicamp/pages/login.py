from bs4 import BeautifulSoup


class LoginPage:
    def __init__(self, html: str):
        self.dom = BeautifulSoup(html)

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
