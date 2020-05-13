import logging
from abc import ABC
from collections import Counter
from pathlib import Path
from typing import Tuple

import attr
from natsort import natsorted, ns

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class BaseRootAggregate(ABC):
    _LOAD_INFO = "* [%s] Loaded '%s' UIDs"
    _PROCESS_INFO = (
        "* [%s] Processed: '%s' files. good: '%s', bad: '%s'. Failed ratio: %.2f%%"
    )
    _ERR_MSG = "Lost data, some indexes were duplicated after merging file: '{f_pth}'"

    @classmethod
    def _from_path(
        cls, root_pth: Path, glob_pattern: str, file_aggregate_cls
    ) -> Tuple[list, dict]:
        def update_index(aggregate):
            len_before = len(index)
            index.update(aggregate.index)
            len_after = len(index)
            if len_after - len_before != len(file_aggregate.index):
                raise RuntimeError(cls._ERR_MSG.format(f_pth=f_pth))

        file_aggregates = []
        index = {}
        all_files = natsorted(root_pth.glob(glob_pattern), alg=ns.PATH)
        c: Counter = Counter(ok=0, error=0, all=len(all_files))
        for i, f_pth in enumerate(all_files):
            try:
                file_aggregate = file_aggregate_cls.from_file(f_pth=f_pth)
                update_index(aggregate=file_aggregate)
                file_aggregates.append(file_aggregate)
                c["ok"] += 1
            except Exception as e:
                log.warning("Error processing: %s, file: '%s', ", e, f_pth)
                c["error"] += 1
            log.trace("Processing file: %s/%s", i, c["all"])
        ratio = (c["error"] / c["all"]) * 100 if c["all"] else 0
        log.info(cls._PROCESS_INFO, cls.__name__, c["all"], c["ok"], c["error"], ratio)
        log.info(cls._LOAD_INFO, cls.__name__, len(index))
        return file_aggregates, index
