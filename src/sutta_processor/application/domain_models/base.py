import json
import logging
import os
import pprint
from abc import ABC, abstractmethod
from collections import Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple

import attr
from natsort import natsorted, ns

from sutta_processor.application.value_objects import UID, RawUID, Verse
from sutta_processor.application.value_objects.verse import VerseTokens
from sutta_processor.shared.exceptions import (
    NoTokensError,
    SegmentIdError,
    SkipFileError,
)

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class BaseVerses(ABC):
    uid: UID = attr.ib(converter=UID, init=False)
    verse: Verse = attr.ib(converter=Verse)

    raw_uid: RawUID = attr.ib(converter=RawUID)

    def __attrs_post_init__(self):
        object.__setattr__(self, "uid", UID(self.raw_uid))


@attr.s(frozen=True, auto_attribs=True)
class BaseFileAggregate(ABC):
    index: Dict[UID, BaseVerses]

    errors: Dict[str, str]

    f_pth: Path
    verses_class = BaseVerses

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
                mn = cls.verses_class(raw_uid=k, verse=v)
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

    def _replace_index(self, index: Dict[UID, BaseVerses]):
        """
        Insecure - won't update the aggregate index. Use only to update file once, and
          then reload the whole thing.
        It will also desynchronize uid&verse.uid
        """
        object.__setattr__(self, "index", index)

    @property
    def data(self) -> Dict[str, str]:
        return {uid: vers.verse for uid, vers in self.index.items()}


@attr.s(frozen=True)
class TextCompareMixin:
    index: Dict[UID, BaseVerses]

    _text_index: Dict[VerseTokens, Set[UID]]
    _text_head_index: Dict[VerseTokens.HeadKey, Set[VerseTokens]]

    @property
    def text_index(self) -> Dict[VerseTokens, Set[UID]]:
        def get_text_index() -> dict:
            text_index = {}
            for uid, verset in self.index.items():
                try:
                    tokens = verset.verse.tokens
                    uids = text_index.get(tokens, set())
                    uids.add(uid)
                    text_index[tokens] = uids
                except NoTokensError as e:
                    log.trace(e)
            return text_index

        if getattr(self, "_text_index", None) is None:
            object.__setattr__(self, "_text_index", get_text_index())
        return self._text_index

    @property
    def text_head_index(self) -> Dict[VerseTokens.HeadKey, Set[VerseTokens]]:
        def get_head_index() -> dict:
            head_index = {}
            for uid, verset in self.index.items():
                try:
                    tokens = verset.verse.tokens
                    all_tokens = head_index.get(tokens.head_key, set())
                    all_tokens.add(tokens)
                    head_index[tokens.head_key] = all_tokens
                except NoTokensError as e:
                    log.trace(e)
            return head_index

        if getattr(self, "_text_head_index", None) is None:
            object.__setattr__(self, "_text_head_index", get_head_index())
        return self._text_head_index


@attr.s(frozen=True, auto_attribs=True)
class BaseRootAggregate(ABC, TextCompareMixin):
    """Translation aggregate has different index structure."""

    index: Dict[UID, BaseVerses]
    file_aggregates: Tuple[BaseFileAggregate]

    _LOAD_INFO = "* [%s] Loaded '%s' UIDs"
    _PROCESS_INFO = "* [%s] Processed: '%s' files. good: '%s', bad: '%s'. Failed ratio: %.2f%%"
    _ERR_MSG = "Lost data, some indexes were duplicated after merging file: '{f_pth}'"

    @classmethod
    def _file_paths_from_dir(cls, exclude_dirs: List[str], root_pth: Path) -> List[Path]:
        """A helper function to get the paths to files contained in the roo_path directory."""
        temp_files = []
        for root_dir, sub_dirs, dir_files in os.walk(root_pth):
            sub_dirs[:] = [d for d in sub_dirs if d not in exclude_dirs]
            temp_files.extend([Path(root_dir + '/' + file) for file in dir_files])

        return temp_files

    @classmethod
    def _file_aggregates_from_files(cls, all_files: List[Path], file_aggregate_cls) -> Tuple[tuple, dict, dict]:
        file_aggregates = []
        index = {}
        errors = {}

        c: Counter = Counter(ok=0, error=0, all=len(all_files))
        for i, f_pth in enumerate(all_files):  # type: int, Path
            try:
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

        return tuple(file_aggregates), index, errors

    @classmethod
    def _from_path(
        cls,
        exclude_dirs: List[str],
        root_pth: Path,
        file_aggregate_cls,
    ) -> Tuple[tuple, dict, dict]:

        temp_files = cls._file_paths_from_dir(exclude_dirs=exclude_dirs, root_pth=root_pth)

        all_files = natsorted(temp_files, alg=ns.PATH)
        file_aggregates, index, errors = cls._file_aggregates_from_files(
            all_files=all_files, file_aggregate_cls=file_aggregate_cls
        )
        if errors:
            msg = "[%s] There are '%s' wrong ids: \n%s"
            keys = pprint.pformat(sorted(errors.keys()))
            log.error(msg, cls.name(), len(errors), keys)

        return tuple(file_aggregates), index, errors

    @classmethod
    def _from_file_paths(
            cls, exclude_dirs: List[str], file_paths: List[Path], file_aggregate_cls, root_langs: List[str] = None,
    ) -> Tuple[tuple, dict, dict]:
        file_aggregates = []
        index = {}
        errors = {}

        all_files = natsorted(file_paths, alg=ns.PATH)
        c: Counter = Counter(ok=0, error=0, all=len(all_files))
        for i, f_pth in enumerate(all_files):  # type: int, Path
            try:
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
