import logging
from pathlib import Path

import attr

from sutta_processor.application.domain_models.base import (
    BaseFileAggregate,
    BaseRootAggregate,
    BaseVersus,
)

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class CommentVersus(BaseVersus):
    pass


@attr.s(frozen=True, auto_attribs=True)
class BilaraCommentFileAggregate(BaseFileAggregate):
    versus_class = CommentVersus

    @classmethod
    def from_dict(cls, in_dto: dict, f_pth: Path) -> "BilaraCommentFileAggregate":
        index, errors = cls._from_dict(in_dto=in_dto)
        return cls(index=index, errors=errors, f_pth=f_pth)


@attr.s(frozen=True, auto_attribs=True, str=False)
class BilaraCommentAggregate(BaseRootAggregate):
    @classmethod
    def from_path(cls, root_pth: Path) -> "BilaraCommentAggregate":
        file_aggregates, index, errors = cls._from_path(
            root_pth=root_pth,
            glob_pattern="**/*.json",
            file_aggregate_cls=BilaraCommentFileAggregate,
        )
        log.info(cls._LOAD_INFO, cls.__name__, len(index))
        return cls(file_aggregates=tuple(file_aggregates), index=index)
