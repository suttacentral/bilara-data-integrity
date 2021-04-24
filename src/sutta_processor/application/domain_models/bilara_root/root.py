import logging
import os
import pprint
from pathlib import Path
from typing import List, Tuple

import attr

from sutta_processor.application.domain_models.base import (
    BaseFileAggregate,
    BaseRootAggregate,
    BaseVerses,
)
from sutta_processor.application.value_objects import RawVerse

from natsort import natsorted, ns

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
    def _file_paths_from_dir(cls, exclude_dirs: List[str], root_pth: Path, root_langs: List[str] = None) -> List[Path]:
        """A helper function to get the paths to files contained in the root_pth directory.
        This function was overridden because it needs to loop through the list of root_langs."""
        temp_files = []
        for lang in root_langs:
            root_lang_path = root_pth / lang
            for root_dir, sub_dirs, dir_files in os.walk(root_lang_path):
                sub_dirs[:] = [d for d in sub_dirs if d not in exclude_dirs]
                temp_files.extend([Path(root_dir + '/' + file) for file in dir_files])

        return temp_files

    @classmethod
    def _from_path(
        cls,
        exclude_dirs: List[str],
        root_pth: Path,
        file_aggregate_cls,
        root_langs: List[str] = None,
    ) -> Tuple[tuple, dict, dict]:
        """An overridden version of _from_path in src/sutta_processor/application/domain_models/base.py.
        This needed to be overridden because of the inclusion of other languages."""
        temp_files = cls._file_paths_from_dir(exclude_dirs=exclude_dirs, root_pth=root_pth, root_langs=root_langs)

        all_files = natsorted(temp_files, alg=ns.PATH)
        # Call parent class' _file_aggregates_from_files
        file_aggregates, index, errors = cls._file_aggregates_from_files(
            all_files=all_files, file_aggregate_cls=file_aggregate_cls
        )
        if errors:
            msg = "[%s] There are '%s' wrong ids: \n%s"
            keys = pprint.pformat(sorted(errors.keys()))
            log.error(msg, cls.name(), len(errors), keys)

        return tuple(file_aggregates), index, errors

    @classmethod
    def from_path(cls, exclude_dirs: List[str], root_pth: Path, root_langs: List[str] = None) -> "BilaraRootAggregate":
        """Calls the overridden version of _from_path defined above."""
        file_aggregates, index, errors = cls._from_path(
            exclude_dirs=exclude_dirs,
            root_pth=root_pth,
            file_aggregate_cls=FileAggregate,
            root_langs=root_langs,
        )
        log.info(cls._LOAD_INFO, cls.__name__, len(index))
        return cls(file_aggregates=tuple(file_aggregates), index=index)

    @classmethod
    def from_file_paths(
        cls, exclude_dirs: List[str], file_paths: List[Path], root_langs: List[str] = None
    ) -> "BilaraRootAggregate":
        """A version of the from_path function that works on a list of files as a pathlib.Path obect."""
        file_aggregates, index, errors = cls._from_file_paths(
            exclude_dirs=exclude_dirs,
            file_paths=file_paths,
            file_aggregate_cls=FileAggregate,
            root_langs=root_langs,
        )
        log.info(cls._LOAD_INFO, cls.__name__, len(index))
        return cls(file_aggregates=tuple(file_aggregates), index=index)
