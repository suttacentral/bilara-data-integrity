from typing import Tuple

import attr

from sutta_processor.application.value_objects import UID, Verse


@attr.s(frozen=True)
class Mn:
    uid: UID = attr.ib(converter=UID)
    raw_root_data: Verse = attr.ib(converter=Verse)


@attr.s(frozen=True, auto_attribs=True)
class MnAggregate:
    parts: Tuple[Mn]

    @classmethod
    def from_dict(cls, in_dto: dict) -> "MnAggregate":
        # TODO: add dict for parts
        # TODO: Check if len of in_dto matches the len of parts_dict
        parts = tuple(Mn(uid=k, raw_root_data=v) for k, v in in_dto.items())
        return cls(parts=parts)
