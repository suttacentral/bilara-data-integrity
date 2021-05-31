import logging
from pathlib import Path
from typing import List

import attr

from sutta_processor.application.domain_models.base import (
    BaseFileAggregate,
    BaseRootAggregate,
    BaseVerses,
)

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class CommentVerses(BaseVerses):
    pass


@attr.s(frozen=True, auto_attribs=True)
class BilaraCommentFileAggregate(BaseFileAggregate):
    verses_class = CommentVerses

    @classmethod
    def from_dict(cls, in_dto: dict, f_pth: Path) -> "BilaraCommentFileAggregate":
        index, errors = cls._from_dict(in_dto=in_dto)
        return cls(index=index, errors=errors, f_pth=f_pth)


@attr.s(frozen=True, auto_attribs=True, str=False)
class BilaraCommentAggregate(BaseRootAggregate):
    @classmethod
    def from_path(cls, exclude_dirs: List[Path], root_pth: Path) -> "BilaraCommentAggregate":
        file_aggregates, index, errors = cls._from_path(
            exclude_dirs=exclude_dirs,
            root_pth=root_pth,
            file_aggregate_cls=BilaraCommentFileAggregate,
        )
        log.info(cls._LOAD_INFO, cls.__name__, len(index))
        return cls(file_aggregates=tuple(file_aggregates), index=index)

    @classmethod
    def from_file_paths(cls, exclude_dirs: List[Path], file_paths: List[Path]) -> "BilaraCommentAggregate":
        file_aggregates, index, errors = cls._from_file_paths(
            exclude_dirs=exclude_dirs,
            file_paths=file_paths,
            file_aggregate_cls=BilaraCommentFileAggregate,
        )
        log.info(cls._LOAD_INFO, cls.__name__, len(index))
        return cls(file_aggregates=tuple(file_aggregates), index=index)