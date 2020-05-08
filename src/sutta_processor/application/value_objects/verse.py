class RawVerse(str):
    def __new__(cls, content: str):
        return super().__new__(cls, content)


class Verse(str):
    def __new__(cls, content: str):
        return super().__new__(cls, content)


class PaliVerse(str):
    def __new__(cls, content: str):
        return super().__new__(cls, content)


class YuttaVerse(PaliVerse):
    def __new__(cls, content: str):
        return super().__new__(cls, content)
