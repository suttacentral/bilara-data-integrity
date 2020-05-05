import logging
from pathlib import Path
from typing import Dict, Tuple

import attr

from sutta_processor.application.value_objects import UID

from .base import PaliFileAggregate, PaliVersus

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True, str=False)
class PaliCanonAggregate:
    files_aggregates: Tuple[PaliFileAggregate]
    index: Dict[UID, PaliVersus]

    _ERR_MSG = "Lost data, some indexes were duplicated after merging file: '{f_pth}'"

    @classmethod
    def from_path(cls, root_pth: Path) -> "PaliCanonAggregate":
        def update_index(aggregate):
            len_before = len(index)
            index.update(aggregate.index)
            len_after = len(index)
            if len_after - len_before != len(file_aggregate.index):
                raise RuntimeError(cls._ERR_MSG.format(f_pth=f_pth))

        files = []
        index = {}
        json_files = root_pth.glob("**/*.html")
        # for f_pth in natsorted(json_files, alg=ns.PATH):
        for f_pth in json_files:
            try:
                file_aggregate = PaliFileAggregate.from_file(f_pth=f_pth)
                # update_index(aggregate=file_aggregate)
                files.append(file_aggregate)
            except Exception as e:
                # TODO [23]: Deal with parsing error
                log.error("Error processing file: '%s', error: %s", f_pth, e)
        log.info(
            "* Loaded '%s' UIDs for '%s'", len(index), cls.__name__,
        )
        log.info("* files parsed: %s", len(files))
        return cls(files_aggregates=tuple(files), index=index)

    def __str__(self):
        return f"<{self.__class__.__name__}, loaded_UIDs: '{len(self.index):,}'>"
