class RawUID(str):
    def __new__(cls, content: str):
        return str.__new__(cls, content)


class UID(str):
    def __new__(cls, content: str):
        return str.__new__(cls, content)
