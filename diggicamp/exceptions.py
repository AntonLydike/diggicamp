class DiggiCampExc(Exception):
    pass


class WebException(DiggiCampExc):
    pass


class DomException(DiggiCampExc):
    pass


class NotLoggedInScepion(WebException):
    def __init__(self):
        super(self, "The user is not logged in!")
