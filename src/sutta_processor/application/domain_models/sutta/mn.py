from typing import Dict, Tuple

import attr

from sutta_processor.application.value_objects import UID, Verse
from sutta_processor.application.value_objects.uid import RawUID
from sutta_processor.application.value_objects.verse import RawVerse


@attr.s(frozen=True, auto_attribs=True)
class Mn:
    uid: UID = attr.ib(converter=UID, init=False)
    verse: Verse = attr.ib(converter=Verse, init=False)

    raw_uid: RawUID = attr.ib(converter=RawUID)
    raw_verse: RawVerse = attr.ib(converter=RawVerse)

    def __attrs_post_init__(self):
        object.__setattr__(self, "uid", self.raw_uid)
        object.__setattr__(self, "verse", self.raw_verse)


@attr.s(frozen=True, auto_attribs=True)
class MnAggregate:
    parts: Tuple[Mn]
    index: Dict[UID, Mn]

    @classmethod
    def from_dict(cls, in_dto: dict) -> "MnAggregate":
        parts = []
        index = {}
        for k, v in in_dto.items():
            mn = Mn(raw_uid=k, raw_verse=v)
            index[mn.uid] = mn
            parts.append(mn)
        if not (len(in_dto) == len(index) == len(parts)):
            raise RuntimeError(f"Lost data during domain model conversion.")
        return cls(parts=tuple(parts), index=index)
