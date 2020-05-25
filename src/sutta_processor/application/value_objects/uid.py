import logging
import re
import string
from itertools import zip_longest
from typing import Union

import attr

from sutta_processor.shared.exceptions import MsIdError, PaliXmlIdError, SegmentIdError

log = logging.getLogger(__name__)


class RawUID(str):
    def __new__(cls, content: str):
        return super().__new__(cls, content)


class Sequence(tuple):
    baked_segment = re.compile(r"\d+?-\d+?")

    @classmethod
    def from_str(cls, raw_seq: str) -> "Sequence":
        raw_seq = raw_seq.split(".")
        args = []
        for segment in raw_seq:
            try:
                args.append(int(segment))
            except ValueError:
                if not cls.baked_segment.match(segment):
                    raise SegmentIdError(f"Invalid uid seq: {raw_seq}")
                args.append(segment)
        return cls(args)

    @property
    def last(self) -> int:
        return int(self[-1])

    @property
    def head(self) -> Union[int, str]:
        return self[0]

    @property
    def second_last(self) -> int:
        return int(self[-2])


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

    def is_next(self, previous: "UidKey"):
        def is_new_file():
            """ Reset sequence when new file. """
            return self.key != previous.key

        def is_same_level():
            return len(self.seq) == len(previous.seq)

        def is_last_1gt():
            return self.seq.last == previous.seq.last + 1

        def is_last_lt():
            """When jumping to next, shorter, block."""
            return self.seq.last < previous.seq.last

        def is_second_last_1gt():
            try:
                return self.seq.second_last == previous.seq.second_last + 1
            except ValueError:
                return False

        def is_level_lt():
            return len(self.seq) < len(previous.seq)

        def is_seq_gt():
            for we, them in zip_longest(self.seq, previous.seq):
                try:
                    if we == them + 1:
                        return True
                except TypeError:
                    # Some are baked: '7-8' and they stay in str
                    return False
            return False

        def is_str_head_in_sequence():
            """Resolve:
            previous: 'mn13:23-28.6' current: 'mn13:29.1'
            Previous: 'mn13:32.5' current: 'mn13:33-35.1'
            Previous: 'mn28:33-34.1' current: 'mn28:35-36.1'
            """
            current_sequence_number = self.seq.head
            previous_sequence_number = previous.seq.head
            if isinstance(current_sequence_number, str):
                current_sequence_number = int(current_sequence_number.split("-")[0])
            if isinstance(previous_sequence_number, str):
                previous_sequence_number = int(previous_sequence_number.split("-")[-1])
            return current_sequence_number == previous_sequence_number + 1

        if is_new_file():
            return True

        if is_same_level():
            if is_last_1gt():
                return True
            if is_second_last_1gt():
                return True
            if is_seq_gt():
                return True
        else:
            if is_seq_gt():
                return True
            if is_level_lt() and is_last_lt():
                # sequence should be shorter and start from 0,1
                return True
        return is_str_head_in_sequence()


class UID(str):
    ALLOWED_SET = set(string.ascii_letters + string.digits + "-:.")

    def __new__(cls, content: str):
        if not set(content).issubset(cls.ALLOWED_SET):
            raise SegmentIdError(f"Invalid uid: '{content}'")
        uid = super().__new__(cls, content)
        uid.key = UidKey(raw=content)
        return uid


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
