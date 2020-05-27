import json
import logging
from pathlib import Path

import attr

from sutta_processor.application.domain_models.base import (
    BaseFileAggregate,
    BaseRootAggregate,
    BaseVersus,
)
from sutta_processor.application.value_objects import UID, Verse
from sutta_processor.application.value_objects.verse import References

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class ConcordanceVersus(BaseVersus):
    uid: UID = attr.ib(init=False)
    verse: Verse

    references: References = attr.ib(init=False)

    def __attrs_post_init__(self):
        object.__setattr__(self, "references", References(self.verse))
        object.__setattr__(self, "verse", Verse(self.verse))
        object.__setattr__(self, "uid", UID(self.raw_uid))


@attr.s(frozen=True, auto_attribs=True)
class ConcordanceFileAggregate(BaseFileAggregate):
    versus_class = ConcordanceVersus

    @classmethod
    def from_dict(cls, in_dto: dict, f_pth: Path) -> "ConcordanceFileAggregate":
        index, errors = cls._from_dict(in_dto=in_dto)
        return cls(index=index, errors=errors, f_pth=f_pth)

    @classmethod
    def from_file(cls, f_pth: Path) -> "BaseFileAggregate":
        with open(f_pth) as f:
            data = json.load(f)
        return cls.from_dict(in_dto=data, f_pth=f_pth)


@attr.s(frozen=True, auto_attribs=True, str=False)
class ConcordanceAggregate(BaseRootAggregate):
    @classmethod
    def from_path(cls, root_pth: Path) -> "ConcordanceAggregate":
        index = {}
        f_aggregate = ConcordanceFileAggregate.from_file(root_pth)
        cls._update_index(index=index, file_aggregate=f_aggregate)
        log.info(cls._LOAD_INFO, cls.__name__, len(index))
        return cls(file_aggregates=(f_aggregate,), index=index)
