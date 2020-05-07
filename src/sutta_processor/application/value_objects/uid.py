 class RawUID(str):
    def __new__(cls, content: str):
        return super().__new__(cls, content)


class UID(str):
    def __new__(cls, content: str):
        return super().__new__(cls, content)


class PaliCrumb(str):
    parts: tuple

    def __new__(cls, content: str):
        """
        Assume type to be the first part of url. Store rest for reference.
        :param content: /tipitaka/1V/1
        """
        pali_type = super().__new__(cls, content)
        pali_type.parts = tuple(content.split("/")[1:])
        return pali_type

    @property
    def type(self) -> str:
        return self.parts[0]


class PaliMsId(str):
    def __new__(cls, content: str):
        return super().__new__(cls, content)


class PaliMsDivId(str):
    def __new__(cls, content: str):
        return super().__new__(cls, content)
