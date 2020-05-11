import logging
from collections import Counter
from pathlib import Path
from typing import Dict, Tuple

import attr
from natsort import natsorted, ns

from sutta_processor.application.value_objects.uid import PaliMsId
from sutta_processor.shared.exceptions import PaliXmlIdError

from .base import YuttaFileAggregate, YuttaVersus

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True, str=False)
class YuttaAggregate:
    file_aggregates: Tuple[YuttaFileAggregate]
    index: Dict[PaliMsId, YuttaVersus]

    _ERR_MSG = "Lost data, some indexes were duplicated after merging file: '{f_pth}'"

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
        msg = "* Processed: '%s' files. good: '%s', bad: '%s'. Failed ratio: %.2f%%"
        ratio = (c["error"] / c["all"]) * 100 if c["all"] else 0
        log.info(msg, c["all"], c["ok"], c["error"], ratio)
        msg = "* Loaded '%s' UIDs for '%s'"
        log.info(msg, len(index), cls.__name__)
        return cls(file_aggregates=tuple(file_aggregates), index=index)

    @classmethod
    def from_path(cls, root_pth: Path) -> "YuttaAggregate":
        def update_index(aggregate):
            len_before = len(index)
            index.update(aggregate.index)
            len_after = len(index)
            if len_after - len_before != len(file_aggregate.index):
                raise RuntimeError(cls._ERR_MSG.format(f_pth=f_pth))

        file_aggregates = []
        index = {}
        all_files = natsorted(root_pth.glob("**/*.html"), alg=ns.PATH)
        c: Counter = Counter(ok=0, error=0, all=len(all_files))
        for i, f_pth in enumerate(all_files):
            try:
                file_aggregate = YuttaFileAggregate.from_file(f_pth=f_pth)
                update_index(aggregate=file_aggregate)
                file_aggregates.append(file_aggregate)
                c["ok"] += 1
            except PaliXmlIdError as e:
                log.trace(e)
                c["ok"] += 1
            except Exception as e:
                log.warning("Error processing: %s, file: '%s', ", e, f_pth)
                c["error"] += 1
            log.trace("Processing file: %s/%s", i, c["all"])

        msg = "* Processed: '%s' files. good: '%s', bad: '%s'. Failed ratio: %.2f%%"
        ratio = (c["error"] / c["all"]) * 100 if c["all"] else 0
        log.info(msg, c["all"], c["ok"], c["error"], ratio)
        msg = "* Loaded '%s' UIDs for '%s'"
        log.info(msg, len(index), cls.__name__)
        return cls(file_aggregates=tuple(file_aggregates), index=index)

    @classmethod
    def name(cls) -> str:
        return cls.__name__

    def __str__(self):
        return f"<{self.__class__.__name__}, loaded_UIDs: '{len(self.index):,}'>"
