import logging
import string

import attr

from sutta_processor.shared.exceptions import MsIdError, PaliXmlIdError

log = logging.getLogger(__name__)


class RawUID(str):
    def __new__(cls, content: str):
        return super().__new__(cls, content)


class Sequence(tuple):
    @classmethod
    def from_str(cls, raw_seq: str) -> "Sequence":
        raw_seq = raw_seq.split(".")
        args = []
        for segment in raw_seq:
            try:
                args.append(int(segment))
            except ValueError:
                args.append(segment)
        return cls(args)


@attr.s(frozen=True, auto_attribs=True)
class UidKey:
    raw: str
    key: str = attr.ib(init=False)
    seq: Sequence = attr.ib(init=False)

    def __attrs_post_init__(self):
        key, raw_seq = self.raw.split(":")
        seq = Sequence.from_str(raw_seq=raw_seq)
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "seq", seq)


class UID(str):

    ALLOWED_SET = set(string.ascii_letters + string.digits + "-:.")

    def __new__(cls, content: str):
        if not set(content).issubset(cls.ALLOWED_SET):
            # TODO: rename exc
            raise RuntimeError(f"Invalid uid: '{content}'")
        uid = super().__new__(cls, content)
        uid.key = UidKey(raw=content)
        return uid

    def is_in_sequence(self, other: "UID") -> bool:

        return True


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
