class RawVerse(str):
    def __new__(cls, content: str):
        return str.__new__(cls, content)


class Verse(str):
    def __new__(cls, content: str):
        return str.__new__(cls, content)
