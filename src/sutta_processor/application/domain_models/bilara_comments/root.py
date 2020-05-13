import json
import logging
from pathlib import Path
from typing import Dict, Tuple

import attr

from sutta_processor.application.domain_models.base import BaseRootAggregate
from sutta_processor.application.value_objects import UID, RawUID, Verse

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class CommentVersus:
    uid: UID = attr.ib(converter=UID, init=False)
    verse: Verse = attr.ib(converter=Verse)

    raw_uid: RawUID = attr.ib(converter=RawUID)

    def __attrs_post_init__(self):
        object.__setattr__(self, "uid", UID(self.raw_uid))


@attr.s(frozen=True, auto_attribs=True)
class BilaraCommentFileAggregate:
    index: Dict[UID, CommentVersus]

    errors: Dict[str, str]

    f_pth: Path

    @classmethod
    def from_dict(cls, in_dto: dict, f_pth: Path) -> "BilaraCommentFileAggregate":
        index = {}
        errors = {}
        for k, v in in_dto.items():
            try:
                mn = CommentVersus(raw_uid=k, verse=v)
                index[mn.uid] = mn
            except Exception as e:
                log.trace(e)
                errors[k] = v
        if not (len(in_dto) == len(index)):
            msg = "Lost '%s' entries during domain model conversion."
            log.error(msg, len(in_dto) - len(index))
        return cls(index=index, f_pth=f_pth, errors=errors)

    @classmethod
    def from_file(cls, f_pth: Path) -> "BilaraCommentFileAggregate":
        with open(f_pth) as f:
            data = json.load(f)
        return cls.from_dict(in_dto=data, f_pth=f_pth)


@attr.s(frozen=True, auto_attribs=True, str=False)
class BilaraCommentAggregate(BaseRootAggregate):
    index: Dict[UID, CommentVersus]
    file_aggregates: Tuple[BilaraCommentFileAggregate]

    _ERR_MSG = "Lost data, some indexes were duplicated after merging file: '{f_pth}'"

    @classmethod
    def from_path(cls, root_pth: Path) -> "BilaraCommentAggregate":
        file_aggregates, index = cls._from_path(
            root_pth=root_pth,
            glob_pattern="**/*.json",
            file_aggregate_cls=BilaraCommentFileAggregate,
        )
        errors = {}
        for aggregate in file_aggregates:  # type: BilaraCommentFileAggregate
            errors.update(aggregate.errors)
        log.error("There are '%s' wrong ids: %s", len(errors), errors.keys())
        return cls(file_aggregates=tuple(file_aggregates), index=index)

    @classmethod
    def name(cls) -> str:
        return cls.__name__

    def __str__(self):
        return f"<{self.name}, loaded_UIDs: '{len(self.index):,}'>"
