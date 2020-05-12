import logging
import string
from itertools import zip_longest
from typing import Union

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

    _sequence_key_exceptions = {
        "dn9:9-10.1",
        "dn9:11.1",
        "dn11:9-66.1",
        "dn11:67.1",
        "dn11:67.1",
        "dn12:20-55.1",
        "dn12:56-62.1",
        "dn12:63-77.1",
        "dn12:78.1",
        "dn13:40-75.0",
        "dn13:76.1",
        "mn9:60-62.1",
        "mn9:59.1",
        "mn9:56-58.1",
        "mn9:55.1",
        "mn9:52-54.1",
        "mn9:51.1",
        "mn9:48-50.1",
        "mn9:47.1",
        "mn9:44-46.1",
        "mn9:43.1",
        "mn9:40-42.1",
        "mn9:39.1",
        "mn9:36-38.1",
        "mn9:35.1",
        "mn9:32-34.1",
        "mn9:31.1",
        "mn9:28-30.1",
        "mn9:27.1",
        "mn9:24-26.1",
        "mn9:23.1",
        "mn9:21-22.1",
        "mn9:19.1",
        "mn9:14-18.1",
        "mn7:17.1",
        "mn7:13-16.1",
        "mn5:28.1",
        "mn5:26-27.1",
        "mn5:25.1",
        "mn5:22-24.1",
        "mn5:21.1",
        "mn5:18-20.1",
        "mn4:27.1",
        "mn4:22-26.1",
        "mn4:8.1",
        "mn4:5-7.1",
        "mn3:9-15.1",
        "mn1:172-194.1",
        "mn1:171.1",
        "mn1:148-170.1",
        "mn1:147.1",
        "mn1:124-146.1",
        "mn1:123.1",
        "mn1:100-122.1",
        "mn1:99.1",
        "mn1:76-98.1",
        "mn1:75.1",
        "mn1:52-74.1",
        "mn1:50.1",
        "mn1:28-49.1",
        "mn19:6.1",
        "mn19:4-5.1",
        "mn17:23.1",
        "mn17:7-22.1",
        "mn13:36.1",
        "mn13:33-35.1",
        "mn13:29.1",
        "mn13:23-28.1",
        "mn12:56.1",
        "mn12:53-55.1",
        "mn10:29.1",
        "mn10:26-28.1",
        "mn10:24.1",
        "mn10:18-23.1",
        "mn9:67.1",
        "mn9:64-66.1",
        "mn9:63.1",
    }

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
                # TODO: except?
                if isinstance(them, str) or isinstance(we, str):
                    return False
                elif them is None or we is None:
                    return False
                elif we == them + 1:
                    return True
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

        # return self.raw in self._sequence_key_exceptions
        # TODO: get error: Previous: 'dn26:21.9' current: 'dn26:21.0'
        return is_str_head_in_sequence()


class UID(str):
    ALLOWED_SET = set(string.ascii_letters + string.digits + "-:.")

    def __new__(cls, content: str):
        if not set(content).issubset(cls.ALLOWED_SET):
            # TODO: rename exc
            raise RuntimeError(f"Invalid uid: '{content}'")
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
