import logging
from pathlib import Path
from typing import Dict

import attr

from sutta_processor.application.value_objects import UID

from .abhidhamma import AbhidhammaAggregate
from .base import Versus
from .sutta import SuttaAggregate
from .vinaya import VinayaAggregate

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True, str=False)
class SuttaCentralAggregate:
    sutta: SuttaAggregate
    abhidhamma: AbhidhammaAggregate
    vinaya: VinayaAggregate

    index: Dict[UID, Versus]

    _ERR_MSG = "Lost data, some indexes were duplicated after merging file: '{f_pth}'"

    @classmethod
    def from_path(cls, root_pth: Path) -> "SuttaCentralAggregate":
        def update_index(aggregate):
            log.debug("** Adding '%s' UIDs to root", aggregate.__class__.__name__)
            len_before = len(index)
            index.update(aggregate.index)
            len_after = len(index)
            if len_after - len_before != len(aggregate.index):
                raise RuntimeError(cls._ERR_MSG.format(f_pth=aggregate.part_pth))

        index = {}
        log.debug("** Loading sutta data")
        sutta = SuttaAggregate.from_path(root_pth=root_pth)
        update_index(aggregate=sutta)

        log.debug("** Loading abhidhamma data")
        abhidhamma = AbhidhammaAggregate.from_path(root_pth=root_pth)
        update_index(aggregate=abhidhamma)

        log.debug("** Loading vinaya data")
        vinaya = VinayaAggregate.from_path(root_pth=root_pth)
        update_index(aggregate=vinaya)

        part_count = (
            len(vinaya.files_aggregates),
            len(abhidhamma.files_aggregates),
            len(sutta.files_aggregates),
        )
        log.debug("** Loaded '%s' files", sum(part_count))
        log.debug("** Root: Loaded all '%s' indexes", len(index))
        kwargs = {
            "sutta": sutta,
            "abhidhamma": abhidhamma,
            "vinaya": vinaya,
            "index": index,
        }
        return cls(**kwargs)

    @classmethod
    def name(cls) -> str:
        return cls.__name__

    def __str__(self):
        return f"<RootAggregate, loaded_UIDs: '{len(self.index):,}'>"
