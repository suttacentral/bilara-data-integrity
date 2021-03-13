import logging
from pathlib import Path
from typing import Dict, List, Tuple

import attr

from sutta_processor.application.domain_models.base import (
    BaseFileAggregate,
    BaseRootAggregate,
    BaseVerses,
)
from sutta_processor.application.value_objects import UID, HtmlVerse

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class HtmlVerses(BaseVerses):
    verse: HtmlVerse = attr.ib(converter=HtmlVerse)


@attr.s(frozen=True, auto_attribs=True)
class BilaraHtmlFileAggregate(BaseFileAggregate):
    verses_class = HtmlVerses

    @classmethod
    def from_dict(cls, in_dto: dict, f_pth: Path) -> "BilaraHtmlFileAggregate":
        index, errors = cls._from_dict(in_dto=in_dto)
        return cls(index=index, errors=errors, f_pth=f_pth)


@attr.s(frozen=True, auto_attribs=True, str=False)
class BilaraHtmlAggregate(BaseRootAggregate):
    index: Dict[UID, HtmlVerses]
    file_aggregates: Tuple[BilaraHtmlFileAggregate]

    file_index: Dict[UID, BilaraHtmlFileAggregate]

    _ERR_MSG = "Lost data, some indexes were duplicated after merging file: '{f_pth}'"

    @classmethod
    def from_path(cls, exclude_dirs: List[str], root_pth: Path) -> "BilaraHtmlAggregate":
        file_aggregates, index, errors = cls._from_path(
            exclude_dirs=exclude_dirs,
            root_pth=root_pth,
            file_aggregate_cls=BilaraHtmlFileAggregate,
        )
        log.info(cls._LOAD_INFO, cls.__name__, len(index))
        file_index = {
            uid: file_aggregate
            for file_aggregate in file_aggregates
            for uid in file_aggregate.index
        }
        # for file_aggregate in file_aggregates:
        #     for uid in file_aggregate.index:
        #         file_index[uid] = file_aggregate
        return cls(file_aggregates=file_aggregates, index=index, file_index=file_index)

    @classmethod
    def from_file_paths(cls, exclude_dirs: List[str], file_paths: List[Path]) -> "BilaraHtmlAggregate":
        """A version of the from_path function that works on a list of files as a pathlib.Path obect."""
        file_aggregates, index, errors = cls._from_file_paths(
            exclude_dirs=exclude_dirs,
            file_paths=file_paths,
            file_aggregate_cls=BilaraHtmlFileAggregate,
        )
        log.info(cls._LOAD_INFO, cls.__name__, len(index))
        file_index = {
            uid: file_aggregate
            for file_aggregate in file_aggregates
            for uid in file_aggregate.index
        }
        # for file_aggregate in file_aggregates:
        #     for uid in file_aggregate.index:
        #         file_index[uid] = file_aggregate
        return cls(file_aggregates=file_aggregates, index=index, file_index=file_index)