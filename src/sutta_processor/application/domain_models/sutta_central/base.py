import json
import logging
from abc import ABC
from pathlib import Path
from typing import Dict, Tuple

import attr
from natsort import natsorted, ns

from sutta_processor.application.value_objects import UID, RawUID, RawVerse, Verse

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class Versus:
    uid: UID = attr.ib(converter=UID, init=False)
    verse: Verse = attr.ib(converter=Verse, init=False)

    raw_uid: RawUID = attr.ib(converter=RawUID)
    raw_verse: RawVerse = attr.ib(converter=RawVerse)

    def __attrs_post_init__(self):
        object.__setattr__(self, "uid", self.raw_uid.strip())
        object.__setattr__(self, "verse", self.raw_verse.strip())


@attr.s(frozen=True, auto_attribs=True)
class FileAggregate:
    parts: Tuple[Versus]
    index: Dict[UID, Versus]

    f_pth: Path

    @classmethod
    def from_dict(cls, in_dto: dict, f_pth: Path) -> "FileAggregate":
        parts = []
        index = {}
        for k, v in in_dto.items():
            mn = Versus(raw_uid=k, raw_verse=v)
            index[mn.uid] = mn
            parts.append(mn)
        if not (len(in_dto) == len(index) == len(parts)):
            raise RuntimeError(f"Lost data during domain model conversion.")
        return cls(parts=tuple(parts), index=index, f_pth=f_pth)

    @classmethod
    def from_file(cls, f_pth: Path) -> "FileAggregate":
        with open(f_pth) as f:
            data = json.load(f)
        return cls.from_dict(in_dto=data, f_pth=f_pth)


@attr.s(frozen=True, auto_attribs=True)
class BaseAggregate(ABC):
    files_aggregates: Tuple[FileAggregate]
    index: Dict[UID, Versus]

    part_pth: Path = attr.ib(init=False)

    _ERR_MSG = "Lost data, some indexes were duplicated after merging file: '{f_pth}'"

    @classmethod
    def from_path(cls, root_pth: Path) -> "BaseAggregate":
        def update_index(aggregate):
            len_before = len(index)
            index.update(aggregate.index)
            len_after = len(index)
            if len_after - len_before != len(file_aggregate.index):
                raise RuntimeError(cls._ERR_MSG.format(f_pth=f_pth))

        files = []
        index = {}
        json_files = (root_pth / cls.part_pth).glob("**/*.json")
        for f_pth in natsorted(json_files, alg=ns.PATH):
            file_aggregate = FileAggregate.from_file(f_pth=f_pth)
            update_index(aggregate=file_aggregate)
            files.append(file_aggregate)
        log.info(
            "* Loaded '%s' UIDs for '%s'", len(index), cls.__name__,
        )
        return cls(files_aggregates=tuple(files), index=index)
