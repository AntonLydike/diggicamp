class DiggiCampExc(Exception):
    pass


class WebException(DiggiCampExc):
    pass


class DomException(DiggiCampExc):
    pass


class CliException(DiggiCampExc):
    def __init__(self, status_code):
        super(CliException, self).__init__(status_code)
        self.status_code: int = status_code


class NotLoggedInScepion(WebException):
    def __init__(self):
        super(self, "The user is not logged in!")
