import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict

import attr

from sutta_processor.application.domain_models.base import (
    BaseFileAggregate,
    BaseRootAggregate,
    BaseVersus,
)
from sutta_processor.application.value_objects import (
    UID,
    BaseTextKey,
    ReferencesConcordance,
    ScID,
    Verse,
)

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class ConcordanceVersus(BaseVersus):
    uid: UID = attr.ib(init=False)
    verse: Verse

    references: ReferencesConcordance = attr.ib(init=False)

    def __attrs_post_init__(self):
        object.__setattr__(self, "references", ReferencesConcordance(self.verse))
        object.__setattr__(self, "verse", Verse(self.verse))
        object.__setattr__(self, "uid", UID(self.raw_uid))


@attr.s(frozen=True, auto_attribs=True)
class ConcordanceFileAggregate(BaseFileAggregate):
    index: Dict[UID, ConcordanceVersus]
    versus_class = ConcordanceVersus

    @classmethod
    def from_dict(cls, in_dto: dict, f_pth: Path) -> "ConcordanceFileAggregate":
        index, errors = cls._from_dict(in_dto=in_dto)
        return cls(index=index, errors=errors, f_pth=f_pth)

    @classmethod
    def from_file(cls, f_pth: Path) -> "BaseFileAggregate":
        with open(f_pth) as f:
            data = json.load(f)
        return cls.from_dict(in_dto=data, f_pth=f_pth)

    @property
    def data(self) -> Dict[str, str]:
        verses = (vers for vers in self.index.values())
        return {v.uid: v.references.data for v in verses}


@attr.s(frozen=True, auto_attribs=True, str=False)
class ConcordanceAggregate(BaseRootAggregate):
    # cs are counted from the first paragraph, but are not unique through whole texts,
    # that's wy we need BaseTextKey to see which sutta it is.
    ref_index: Dict[BaseTextKey, Dict[ScID, list]]

    @classmethod
    def from_path(cls, root_pth: Path) -> "ConcordanceAggregate":
        index = {}
        f_aggregate = ConcordanceFileAggregate.from_file(root_pth)
        cls._update_index(index=index, file_aggregate=f_aggregate)
        log.info(cls._LOAD_INFO, cls.__name__, len(index))

        ref_index = defaultdict(dict)
        for uid, versus in index.items():  # type: UID, ConcordanceVersus
            if not versus.references.sc_id:
                log.error("Concordance uid: '%s' des not have sc ref", uid)
                continue
            ref_index[uid.key.key][versus.references.sc_id] = versus.references
        return cls(
            file_aggregates=(f_aggregate,), index=index, ref_index=dict(ref_index)
        )
