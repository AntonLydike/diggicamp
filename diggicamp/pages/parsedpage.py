from bs4 import BeautifulSoup


class ParsedPage:
    def __init__(self, html: str):
        self.dom = BeautifulSoup(html, "html.parser")
