import logging
from pathlib import Path
from typing import Dict

import attr
from natsort import natsorted

from sutta_processor.application.domain_models.base import (
    BaseFileAggregate,
    BaseRootAggregate,
    BaseVerses,
)
from sutta_processor.application.value_objects import UID, References, Verse

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class ReferenceVerses(BaseVerses):
    uid: UID = attr.ib(init=False)
    verse: Verse

    references: References = attr.ib(init=False)

    def __attrs_post_init__(self):
        object.__setattr__(self, "references", References(self.verse))
        object.__setattr__(self, "verse", Verse(self.verse))
        object.__setattr__(self, "uid", UID(self.raw_uid))


@attr.s(frozen=True, auto_attribs=True)
class BilaraReferenceFileAggregate(BaseFileAggregate):
    verses_class = ReferenceVerses
    index: Dict[UID, ReferenceVerses]

    @classmethod
    def from_dict(cls, in_dto: dict, f_pth: Path) -> "BilaraReferenceFileAggregate":
        index, errors = cls._from_dict(in_dto=in_dto)
        return cls(index=index, errors=errors, f_pth=f_pth)

    @property
    def data(self) -> Dict[str, str]:
        verses = (vers for vers in self.index.values())
        return {v.uid: v.references.data for v in verses}

    @property
    def data_sorted(self) -> Dict[str, str]:
        key_order = natsorted(self.index)
        verses = (self.index[uid] for uid in key_order)
        return {v.uid: v.references.data for v in verses}


@attr.s(frozen=True, auto_attribs=True, str=False)
class BilaraReferenceAggregate(BaseRootAggregate):
    index: Dict[UID, ReferenceVerses]

    @classmethod
    def from_path(cls, root_pth: Path) -> "BilaraReferenceAggregate":
        file_aggregates, index, errors = cls._from_path(
            root_pth=root_pth,
            file_aggregate_cls=BilaraReferenceFileAggregate,
        )
        log.info(cls._LOAD_INFO, cls.__name__, len(index))
        return cls(file_aggregates=tuple(file_aggregates), index=index)
