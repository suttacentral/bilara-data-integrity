import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set

from sutta_processor.application.domain_models import (
    PaliCanonAggregate,
    SuttaCentralAggregate,
)
from sutta_processor.application.value_objects import UID, MsId
from sutta_processor.application.value_objects.uid import UidKey
from sutta_processor.shared.config import Config
from sutta_processor.shared.exceptions import MsIdError, MultipleIdFoundError

log = logging.getLogger(__name__)


class CheckEngine:
    uid_index: Dict[UID, MsId]
    ms_id_index: Dict[MsId, Set[UID]]

    _ERR_MSG = "Lost data, some indexes were duplicated after merging file: '{f_pth}'"

    def __init__(self, cfg: Config):
        self.cfg = cfg
        raw_index: dict = self.get_raw_index_from_path(
            reference_root_path=cfg.reference_root_path
        )
        self.uid_index = self.get_uid_index(raw_index=raw_index)
        self.ms_id_index = self.get_ms_id_index(uid_index=self.uid_index)

        if len(self.uid_index) != len(self.ms_id_index):
            msg = "uid->pali and pali->uid indexes are different lengths. '%s' vs '%s'"
            log.warning(msg, len(self.uid_index), len(self.ms_id_index))

    @classmethod
    def get_ms_id_index(cls, uid_index: Dict[UID, MsId]) -> Dict[MsId, Set[UID]]:
        pali_id_index = defaultdict(set)
        for k, v in uid_index.items():
            pali_id_index[v].add(k)

        for pali_id, uid_set in pali_id_index.items():
            if len(uid_set) != 1:
                msg = "Pali_ms_id '%s' is referencing several SuttaCentral uid: %s"
                log.error(msg, pali_id, uid_set)

        return pali_id_index

    @classmethod
    def get_uid_index(cls, raw_index: dict) -> Dict[UID, MsId]:
        def get_pali_ms_id(reference_value: str) -> MsId:
            """
            :param reference_value: sc2, pts-cs1.1, pts-vp-en1.1, pts-vp-pli3.1, ms1V_2
            """
            pali_id_set = set()
            for item in reference_value.split(","):
                try:
                    pali_id_set.add(MsId(item.strip()))
                except MsIdError:
                    # Filter out any non MsIds
                    pass
            if len(pali_id_set) > 1:
                msg = f"More than one MsId reference found: '{reference_value}'"
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


class BDataCheckService:
    _check_engine: CheckEngine = None

    def __init__(self, cfg: Config):
        self.cfg = cfg

    def check_uid_sequence_in_file(self, aggregate: SuttaCentralAggregate):
        error_keys = set()
        previous_elem = UidKey(":")
        for idx in aggregate.index:
            if not idx.key.is_next(previous=previous_elem):
                error_keys.add(idx)
                msg = "[%s] Sequence error. Previous: '%s' current: '%s'"
                log.error(msg, self.__class__.__name__, previous_elem.raw, idx)
            previous_elem = idx.key
        if error_keys:
            msg = "[%s] There are '%s' sequence key errors"
            log.error(msg, self.__class__.__name__, len(error_keys))

    @property
    def check_engine(self) -> CheckEngine:
        if not self._check_engine:
            self._check_engine = CheckEngine(cfg=self.cfg)
        return self._check_engine
