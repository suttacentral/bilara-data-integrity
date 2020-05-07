import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set

from sutta_processor.application.domain_models.pali_canon.root import PaliCanonAggregate
from sutta_processor.application.value_objects import UID
from sutta_processor.application.value_objects.uid import PaliMsId
from sutta_processor.shared.config import Config
from sutta_processor.shared.exceptions import MultipleIdFoundError, PaliMsIdError

log = logging.getLogger(__name__)


class ReferenceEngine:
    uid_index: Dict[UID, PaliMsId]
    pali_id_index: Dict[PaliMsId, Set[UID]]

    _ERR_MSG = "Lost data, some indexes were duplicated after merging file: '{f_pth}'"

    def __init__(self, cfg: Config):
        self.cfg = cfg
        raw_index: dict = self.get_raw_index_from_path(
            reference_root_path=cfg.reference_root_path
        )
        self.uid_index = self.get_uid_index(raw_index=raw_index)
        self.pali_id_index = self.get_pali_id_index(uid_index=self.uid_index)

        if len(self.uid_index) != len(self.pali_id_index):
            msg = "uid->pali and pali->uid indexes are different lengths. '%s' vs '%s'"
            log.warning(msg, len(self.uid_index), len(self.pali_id_index))

    @classmethod
    def get_pali_id_index(
        cls, uid_index: Dict[UID, PaliMsId]
    ) -> Dict[PaliMsId, Set[UID]]:
        pali_id_index = defaultdict(set)
        for k, v in uid_index.items():
            pali_id_index[v].add(k)

        for pali_id, uid_set in pali_id_index.items():
            if len(uid_set) != 1:
                msg = "Pali_ms_id '%s' is referencing several SuttaCentral uid: %s"
                log.error(msg, pali_id, uid_set)

        return pali_id_index

    @classmethod
    def get_uid_index(cls, raw_index: dict) -> Dict[UID, PaliMsId]:
        def get_pali_ms_id(reference_value: str) -> PaliMsId:
            """
            :param reference_value: sc2, pts-cs1.1, pts-vp-en1.1, pts-vp-pli3.1, ms1V_2
            """
            pali_id_set = set()
            for item in reference_value.split(","):
                try:
                    pali_id_set.add(PaliMsId(item.strip()))
                except PaliMsIdError:
                    # Filter out any non PaliMsIds
                    pass
            if len(pali_id_set) > 1:
                msg = f"More than one PaliMsId reference found: '{reference_value}'"
                raise MultipleIdFoundError(msg)
            return pali_id_set.pop()

        index = {}
        for uid, sources in raw_index.items():  # type: str, str
            try:
                index[UID(uid)] = get_pali_ms_id(reference_value=sources)
            except MultipleIdFoundError:
                msg = "SuttaCentral uid '%s' is referencing several pali sources: %s"
                log.error(msg, uid, sources)
            except KeyError:
                # No reference found for that UID
                pass
        return index

    @classmethod
    def get_raw_index_from_path(cls, reference_root_path: Path) -> dict:
        """
        :return: {
          "pli-tv-bu-vb-pj1:1.1.0": "sc1, ms1V_1",
          "pli-tv-bu-vb-pj1:1.1.1": "sc2, pts-cs1.1, pts-vp-en1.1, pts-vp-pli3.1, ms1V_2",
          "pli-tv-bu-vb-pj1:1.2.1": "pts-vp-pli3.2, sc3, pts-cs1.2, ms1V_3",
          "pli-tv-bu-vb-pj1:1.3.1": "sc5, pts-cs1.3, ms1V_5",
          ...
          }
        """
        raw_index = {}
        len_before = 0
        for f_pth in reference_root_path.glob("**/*.json"):
            with open(f_pth) as f:
                data = json.load(f)

            raw_index.update(data)
            len_after = len(raw_index)
            if len_after - len_before != len(data):
                raise RuntimeError(cls._ERR_MSG.format(f_pth=f_pth))
            len_before = len_after
        return raw_index


class SCReferenceService:
    _reference_engine: ReferenceEngine = None

    def __init__(self, cfg: Config):
        self.cfg = cfg

    def log_missing_pali_id_from_reference(self, pali_aggregate: PaliCanonAggregate):
        diff = {
            k
            for k in pali_aggregate.index
            if k not in self.reference_engine.pali_id_index
        }
        if diff:
            msg = "There are '%s' PaliMsID that are not found in the reference file"
            log.error(msg, len(diff))
            log.error("Missing PaliMsID from reference: %s", diff)

    @property
    def reference_engine(self) -> ReferenceEngine:
        if not self._reference_engine:
            self._reference_engine = ReferenceEngine(cfg=self.cfg)
        return self._reference_engine
