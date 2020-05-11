from sutta_processor.shared.exceptions import MsIdError, PaliXmlIdError


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


class MsId(str):
    XML_ID_P = "p_"  # Used in original XML docs
    XML_ID_H = "h_"
    MS_ID = "ms"  # Used everywhere else to reference this source

    def __new__(cls, content: str):
        """
        :param content: ms1V_1
        """
        if not content.startswith(cls.MS_ID) or ("div" in content):
            raise MsIdError(f"'{content}' is not valid ms id")
        return super().__new__(cls, content)

    @classmethod
    def from_xml_id(cls, content: str) -> "MsId":
        """
        :param content: p_1V_1
        """
        content = content.strip()
        if content.startswith(cls.XML_ID_P) or content.startswith(cls.XML_ID_H):
            return cls(f"{cls.MS_ID}{content[2:]}")
        raise PaliXmlIdError(f"'{content}' is not valid xml id")

    @property
    def stem(self) -> str:
        return self.replace(self.MS_ID, "", 1)


class PaliMsDivId(str):
    def __new__(cls, content: str):
        return super().__new__(cls, content)
