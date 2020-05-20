import json
import logging
import pprint
from abc import ABC, abstractmethod
from collections import Counter
from pathlib import Path
from typing import Dict, Tuple

import attr
from natsort import natsorted, ns

from sutta_processor.application.value_objects import UID, RawUID, Verse
from sutta_processor.shared.exceptions import SegmentIdError, SkipFileError

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class BaseVersus(ABC):
    uid: UID = attr.ib(converter=UID, init=False)
    verse: Verse = attr.ib(converter=Verse)

    raw_uid: RawUID = attr.ib(converter=RawUID)

    def __attrs_post_init__(self):
        object.__setattr__(self, "uid", UID(self.raw_uid))


@attr.s(frozen=True, auto_attribs=True)
class BaseFileAggregate(ABC):
    index: Dict[UID, BaseVersus]

    errors: Dict[str, str]

    f_pth: Path
    versus_class = BaseVersus

    @classmethod
    @abstractmethod
    def from_dict(cls, in_dto: dict, f_pth: Path):
        pass

    @classmethod
    def _from_dict(cls, in_dto: dict) -> Tuple[dict, dict]:
        index = {}
        errors = {}
        for k, v in in_dto.items():
            try:
                mn = cls.versus_class(raw_uid=k, verse=v)
                index[mn.uid] = mn
            except SegmentIdError as e:
                log.trace(e)
                errors[k] = v
        if not (len(in_dto) == len(index)):
            diff = in_dto.keys() - index.keys()
            msg = "Lost '%s' entries during domain model conversion: %s"
            log.error(msg, len(diff), diff)
        return index, errors

    @classmethod
    def from_file(cls, f_pth: Path) -> "BaseFileAggregate":
        with open(f_pth) as f:
            data = json.load(f)
        return cls.from_dict(in_dto=data, f_pth=f_pth)

    @property
    def data(self) -> Dict[str, str]:
        verses = (vers for vers in self.index.values())
        return {v.uid: v.verse for v in verses}


@attr.s(frozen=True, auto_attribs=True)
class BaseRootAggregate(ABC):
    """Translation aggregate has different index structure."""

    index: Dict[UID, BaseVersus]
    file_aggregates: Tuple[BaseFileAggregate]

    _LOAD_INFO = "* [%s] Loaded '%s' UIDs"
    _PROCESS_INFO = (
        "* [%s] Processed: '%s' files. good: '%s', bad: '%s'. Failed ratio: %.2f%%"
    )
    _ERR_MSG = "Lost data, some indexes were duplicated after merging file: '{f_pth}'"

    @classmethod
    def _from_path(
        cls, root_pth: Path, glob_pattern: str, file_aggregate_cls
    ) -> Tuple[tuple, dict, dict]:
        file_aggregates = []
        index = {}
        errors = {}
        all_files = natsorted(root_pth.glob(glob_pattern), alg=ns.PATH)
        c: Counter = Counter(ok=0, error=0, all=len(all_files))
        for i, f_pth in enumerate(all_files):
            try:
                if "xplayground" in f_pth.parts:
                    raise SkipFileError()
                file_aggregate = file_aggregate_cls.from_file(f_pth=f_pth)
                cls._update_index(index=index, file_aggregate=file_aggregate)
                errors.update(file_aggregate.errors)
                file_aggregates.append(file_aggregate)
                c["ok"] += 1
            except SkipFileError:
                c["all"] -= 1
            except Exception as e:
                log.warning("Error processing: %s, file: '%s', ", e, f_pth)
                c["error"] += 1
            log.trace("Processing file: %s/%s", i, c["all"])
        ratio = (c["error"] / c["all"]) * 100 if c["all"] else 0
        log.info(cls._PROCESS_INFO, cls.name(), c["all"], c["ok"], c["error"], ratio)
        if errors:
            msg = "[%s] There are '%s' wrong ids: \n%s"
            keys = pprint.pformat(sorted(errors.keys()))
            log.error(msg, cls.name(), len(errors), keys)
        return tuple(file_aggregates), index, errors

    @classmethod
    def _update_index(cls, index: dict, file_aggregate: BaseFileAggregate):
        len_before = len(index)
        index.update(file_aggregate.index)
        len_after = len(index)
        if len_after - len_before != len(file_aggregate.index):
            raise RuntimeError(cls._ERR_MSG.format(f_pth=file_aggregate.f_pth))

    @classmethod
    def name(cls) -> str:
        return cls.__name__

    def __str__(self):
        return f"<{self.name()}, loaded_UIDs: '{len(self.index):,}'>"
