import json
import logging
from pathlib import Path
from typing import Dict, Tuple

import attr

from sutta_processor.application.domain_models.base import BaseRootAggregate
from sutta_processor.application.value_objects import UID, RawUID, Verse

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class VariantVersus:
    uid: UID = attr.ib(converter=UID, init=False)
    verse: Verse = attr.ib(converter=Verse)

    raw_uid: RawUID = attr.ib(converter=RawUID)

    def __attrs_post_init__(self):
        object.__setattr__(self, "uid", UID(self.raw_uid))


@attr.s(frozen=True, auto_attribs=True)
class BilaraVariantFileAggregate:
    index: Dict[UID, VariantVersus]

    errors: Dict[str, str]

    f_pth: Path

    @classmethod
    def from_dict(cls, in_dto: dict, f_pth: Path) -> "BilaraVariantFileAggregate":
        index = {}
        errors = {}
        for k, v in in_dto.items():
            try:
                mn = VariantVersus(raw_uid=k, verse=v)
                index[mn.uid] = mn
            except Exception as e:
                log.trace(e)
                errors[k] = v
        if not (len(in_dto) == len(index)):
            diff = in_dto.keys() - index.keys()
            msg = "Lost '%s' entries during domain model conversion: %s"
            log.error(msg, len(diff), diff)
        return cls(index=index, f_pth=f_pth, errors=errors)

    @classmethod
    def from_file(cls, f_pth: Path) -> "BilaraVariantFileAggregate":
        with open(f_pth) as f:
            data = json.load(f)
        return cls.from_dict(in_dto=data, f_pth=f_pth)


@attr.s(frozen=True, auto_attribs=True, str=False)
class BilaraVariantAggregate(BaseRootAggregate):
    index: Dict[UID, VariantVersus]
    file_aggregates: Tuple[BilaraVariantFileAggregate]

    _ERR_MSG = "Lost data, some indexes were duplicated after merging file: '{f_pth}'"

    @classmethod
    def from_path(cls, root_pth: Path) -> "BilaraVariantAggregate":
        file_aggregates, index = cls._from_path(
            root_pth=root_pth,
            glob_pattern="**/*.json",
            file_aggregate_cls=BilaraVariantFileAggregate,
        )
        errors = {}
        for aggregate in file_aggregates:  # type: BilaraVariantFileAggregate
            errors.update(aggregate.errors)
        if errors:
            log.error("There are '%s' wrong ids: %s", len(errors), errors.keys())
        return cls(file_aggregates=tuple(file_aggregates), index=index)

    @classmethod
    def name(cls) -> str:
        return cls.__name__

    def __str__(self):
        return f"<{self.name}, loaded_UIDs: '{len(self.index):,}'>"
