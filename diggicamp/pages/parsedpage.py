from bs4 import BeautifulSoup, UnicodeDammit


def unicode(input: str) -> str:
    return UnicodeDammit(input).unicode_markup


class ParsedPage:
    def __init__(self, html: str):
        self.dom = BeautifulSoup(html, "lxml")
