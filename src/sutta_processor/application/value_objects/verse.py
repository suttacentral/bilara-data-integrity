class RawVerse(str):
    def __new__(cls, content: str):
        return super().__new__(cls, content)


class Verse(str):
    def __new__(cls, content: str):
        return super().__new__(cls, content)


class HtmlVerse(str):
    def __new__(cls, content: str):
        return super().__new__(cls, content)


class MsVerse(str):
    def __new__(cls, content: str):
        return super().__new__(cls, content)
