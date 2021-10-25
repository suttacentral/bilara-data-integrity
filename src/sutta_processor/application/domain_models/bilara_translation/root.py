import logging
from pathlib import Path
from typing import Dict, List, Tuple

import attr

from sutta_processor.application.domain_models.base import (
    BaseFileAggregate,
    BaseRootAggregate,
    BaseVerses,
)
from sutta_processor.application.value_objects import UID

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class TranslationVerses(BaseVerses):
    pass


@attr.s(frozen=True, auto_attribs=True)
class BilaraTranslationFileAggregate(BaseFileAggregate):
    verses_class = TranslationVerses

    @classmethod
    def from_dict(cls, in_dto: dict, f_pth: Path) -> "BilaraTranslationFileAggregate":
        index, errors = cls._from_dict(in_dto=in_dto)
        return cls(index=index, errors=errors, f_pth=f_pth)


@attr.s(frozen=True, auto_attribs=True, str=False)
class BilaraTranslationAggregate(BaseRootAggregate):
    index: Dict[str, Dict[UID, TranslationVerses]]
    file_aggregates: Tuple[BilaraTranslationFileAggregate]

    _ERR_MSG = "Lost data, some indexes were duplicated after merging file: '{f_pth}'"

    @classmethod
    def from_path(cls, exclude_dirs: List[Path], root_pth: Path) -> "BilaraCommentAggregate":
        file_aggregates, index, errors = cls._from_path(
            exclude_dirs=exclude_dirs,
            root_pth=root_pth,
            file_aggregate_cls=BilaraTranslationFileAggregate,
        )
        length = 0
        for lang_dict in index.values():
            length += len(lang_dict)
        log.info(cls._LOAD_INFO, cls.__name__, length)
        return cls(file_aggregates=file_aggregates, index=index)

    @classmethod
    def from_file_paths(cls, exclude_dirs: List[Path], file_paths: List[Path]) -> "BilaraCommentAggregate":
        file_aggregates, index, errors = cls._from_file_paths(
            exclude_dirs=exclude_dirs,
            file_paths=file_paths,
            file_aggregate_cls=BilaraTranslationFileAggregate,
        )
        length = 0
        for lang_dict in index.values():
            length += len(lang_dict)
        log.info(cls._LOAD_INFO, cls.__name__, length)
        return cls(file_aggregates=file_aggregates, index=index)

    @classmethod
    def _update_index(cls, index: dict, file_aggregate):
        def get_lang() -> str:
            for part in file_aggregate.f_pth.parts:
                if part in {'cs', 'de', 'en', 'id', 'jpn', 'my', 'pt', 'vi'}:
                    return part
            raise RuntimeError('No language detected')

        lang = get_lang()
        lang_index = index.get(lang, {})
        if not lang_index:
            index[lang] = lang_index
        len_before = len(lang_index)
        lang_index.update(file_aggregate.index)
        len_after = len(lang_index)
        if len_after - len_before != len(file_aggregate.index):
            raise RuntimeError(cls._ERR_MSG.format(f_pth=file_aggregate.f_pth))

    def __str__(self):
        length = 0
        for lang_dict in self.index.values():
            length += len(lang_dict)
        return f"<{self.name()}, loaded_UIDs: '{length:,}'>"
