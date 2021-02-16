import logging
from pathlib import Path
from typing import Dict, Tuple

import attr

from sutta_processor.application.domain_models.base import (
    BaseFileAggregate,
    BaseRootAggregate,
    BaseVerses,
)
from sutta_processor.application.value_objects import UID

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class VariantVerses(BaseVerses):
    pass


@attr.s(frozen=True, auto_attribs=True)
class BilaraVariantFileAggregate(BaseFileAggregate):
    verses_class = VariantVerses

    @classmethod
    def from_dict(cls, in_dto: dict, f_pth: Path) -> "BilaraVariantFileAggregate":
        index, errors = cls._from_dict(in_dto=in_dto)
        return cls(index=index, errors=errors, f_pth=f_pth)


@attr.s(frozen=True, auto_attribs=True, str=False)
class BilaraVariantAggregate(BaseRootAggregate):
    index: Dict[UID, VariantVerses]
    file_aggregates: Tuple[BilaraVariantFileAggregate]

    _ERR_MSG = "Lost data, some indexes were duplicated after merging file: '{f_pth}'"

    @classmethod
    def from_path(cls, root_pth: Path) -> "BilaraCommentAggregate":
        file_aggregates, index, errors = cls._from_path(
            root_pth=root_pth,
            file_aggregate_cls=BilaraVariantFileAggregate,
        )
        log.info(cls._LOAD_INFO, cls.__name__, len(index))
        return cls(file_aggregates=tuple(file_aggregates), index=index)
