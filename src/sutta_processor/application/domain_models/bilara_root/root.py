import logging
from pathlib import Path

import attr

from sutta_processor.application.domain_models.base import (
    BaseFileAggregate,
    BaseRootAggregate,
    BaseVerses,
)
from sutta_processor.application.value_objects import RawVerse

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class Verses(BaseVerses):
    raw_verse: RawVerse = attr.ib(converter=RawVerse, init=False)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        object.__setattr__(self, "raw_verse", RawVerse(self.verse))


@attr.s(frozen=True, auto_attribs=True)
class FileAggregate(BaseFileAggregate):
    verses_class = Verses

    @classmethod
    def from_dict(cls, in_dto: dict, f_pth: Path) -> "FileAggregate":
        index, errors = cls._from_dict(in_dto=in_dto)
        return cls(index=index, f_pth=f_pth, errors=errors)


@attr.s(frozen=True, auto_attribs=True, str=False)
class BilaraRootAggregate(BaseRootAggregate):
    @classmethod
    def from_path(cls, root_pth: Path) -> "BilaraRootAggregate":
        file_aggregates, index, errors = cls._from_path(
            root_pth=root_pth,
            glob_pattern="**/*.json",
            file_aggregate_cls=FileAggregate,
        )
        log.info(cls._LOAD_INFO, cls.__name__, len(index))
        return cls(file_aggregates=tuple(file_aggregates), index=index)
