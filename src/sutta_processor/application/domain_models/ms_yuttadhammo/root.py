import logging
from collections import Counter
from pathlib import Path
from typing import Dict, Set, Tuple

import attr
from natsort import natsorted, ns

from sutta_processor.application.domain_models.base import BaseRootAggregate
from sutta_processor.application.value_objects import MsId

from ...value_objects.verse import VerseTokens
from .base import YuttaFileAggregate, YuttaVersus

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True, str=False)
class YuttaAggregate(BaseRootAggregate):
    file_aggregates: Tuple[YuttaFileAggregate]
    index: Dict[MsId, YuttaVersus]

    _text_index: Dict[VerseTokens, Set[MsId]]
    _text_head_index: Dict[VerseTokens.HeadKey, Set[VerseTokens]]

    @classmethod
    def from_path(cls, root_pth: Path) -> "YuttaAggregate":
        file_aggregates, index, errors = cls._from_path(
            root_pth=root_pth,
            glob_pattern="**/*.html",
            file_aggregate_cls=YuttaFileAggregate,
        )
        return cls(file_aggregates=tuple(file_aggregates), index=index)

    @classmethod
    def name(cls) -> str:
        return cls.__name__

    def __str__(self):
        return f"<{self.__class__.__name__}, loaded_UIDs: '{len(self.index):,}'>"

    @classmethod
    def convert_to_html(cls, root_pth: Path) -> "YuttaAggregate":
        """
        This will only load xml and extract from it the html content.
        Save both contents in raw_* attribs.
        """
        file_aggregates = []
        index = {}
        all_files = natsorted(root_pth.glob("**/*.xml"), alg=ns.PATH)
        c: Counter = Counter(ok=0, error=0, all=len(all_files))
        for i, f_pth in enumerate(all_files):
            try:
                file_aggregate = YuttaFileAggregate.convert_to_html(f_pth=f_pth)
                file_aggregates.append(file_aggregate)
                c["ok"] += 1
            except Exception as e:
                log.warning("Error processing: %s, file: '%s', ", e, f_pth)
                c["error"] += 1
            log.trace("Processing file: %s/%s", i, c["all"])
        ratio = (c["error"] / c["all"]) * 100 if c["all"] else 0
        log.info(cls._PROCESS_INFO, cls.__name__, c["all"], c["ok"], c["error"], ratio)
        log.info(cls._LOAD_INFO, cls.__name__, len(index))
        return cls(file_aggregates=tuple(file_aggregates), index=index)
