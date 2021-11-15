import json
import logging
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Set

from sutta_processor.application.domain_models import (
    BilaraHtmlAggregate,
    BilaraReferenceAggregate,
    BilaraRootAggregate,
    YuttaAggregate,
)
from sutta_processor.application.domain_models.base import BaseFileAggregate
from sutta_processor.application.domain_models.bilara_reference.root import (
    ReferenceVerses,
)
from sutta_processor.application.value_objects import UID, BaseTextKey, MsId
from sutta_processor.shared.config import Config
from sutta_processor.shared.exceptions import MsIdError, MultipleIdFoundError

log = logging.getLogger(__name__)


class ReferenceEngine:
    uid_index: Dict[UID, MsId]
    ms_id_index: Dict[MsId, Set[UID]]

    uid_reference: Dict[UID, Set[str]]

    _ERR_MSG = "Lost data, some indexes were duplicated after merging file: '{f_pth}'"

    def __init__(self, cfg: Config):
        self.cfg = cfg
        raw_index: dict = self.get_raw_index_from_path(
            reference_root_path=cfg.reference_root_path
        )
        self.uid_index = self.get_uid_index(raw_index=raw_index)
        self.ms_id_index = self.get_ms_id_index(uid_index=self.uid_index)
        self.uid_reference = self.get_uid_reference(raw_index=raw_index)

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

        return dict(pali_id_index)

    # LOOK AT ME
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
                try:
                    data = json.load(f)
                except Exception as e:
                    log.error("Error loading file '%s'. Error: %s", f_pth, e)
                    raise

            raw_index.update(data)
            len_after = len(raw_index)
            if len_after - len_before != len(data):
                raise RuntimeError(cls._ERR_MSG.format(f_pth=f_pth))
            len_before = len_after
        return raw_index

    @classmethod
    def get_uid_reference(cls, raw_index: Dict[str, str]) -> Dict[UID, Set[str]]:
        def get_sources_set(reference_value: str) -> Set[str]:
            """
            :param reference_value: sc2, pts-cs1.1, pts-vp-en1.1, pts-vp-pli3.1, ms1V_2
            """
            pali_id_set = set()
            for item in reference_value.split(","):
                pali_id_set.add(item.strip())
            return pali_id_set

        index = {}
        for uid, sources in raw_index.items():  # type: str, str
            index[UID(uid)] = get_sources_set(reference_value=sources)
        return index


class SCReferenceService:
    reference_engine: ReferenceEngine
    _MS_REF_MISS_COUNT = (
        "[%s] There are '%s' MsId that are not found in the reference file"
    )
    _MS_REF_MISS = "[%s] Missing MsId from reference: %s"
    _MS_WRONG_COUNT = "[%s] There are '%s' wrong MsId in the reference data"
    _MS_WRONG = "[%s] Wrong MsId is the reference data: %s"
    _UID_WRONG_COUNT = "[%s] There are '%s' wrong SC UID in the reference data"
    _UID_WRONG = "[%s] Wrong SC UID is the reference data: %s"

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.reference_engine = ReferenceEngine(cfg=cfg)

    def get_duplicated_ms_id(self, reference: BilaraReferenceAggregate):
        def get_reference_counts() -> Counter:
            c: Counter = Counter()
            for verse in reference.index.values():
                for ref in verse.references:
                    if not isinstance(ref, MsId):
                        continue
                    c[ref] += 1
            return c

        def get_surplus_ref(c: Counter) -> dict:
            """
            :return: {count: ms_ref_list]
            """
            duplicates = defaultdict(list)
            for ms_id, count in c.items():
                duplicates[count].append(ms_id)
            duplicates.pop(1)
            return duplicates

        counter = get_reference_counts()
        # Take into account when there might be references that don't have ms_ids, like Chinese texts.
        if counter:
            duplicated_ms_id = get_surplus_ref(c=counter)

            if duplicated_ms_id:
                omg = "[%s] There are '%s' duplicated ms_id in bilara references: %s"
                log.error(omg, self.name, len(duplicated_ms_id[2]), duplicated_ms_id[2])
                duplicated_ms_id.pop(2)
                if duplicated_ms_id:
                    omg = "[%s] There are multiple ms_id in bilara references: %s"
                    log.error(omg, self.name, duplicated_ms_id)

    @classmethod
    def get_references_stem(cls, reference: BilaraReferenceAggregate) -> list:
        stems = set()
        for verse in reference.index.values():  # type: ReferenceVerses
            stems.update((v.reference_root for v in verse.references))
        reference_stems = list(sorted(stems))
        log.error("Reference stems: %s", reference_stems)
        return reference_stems

    def get_wrong_pts_cs_no(self, reference: BilaraReferenceAggregate):
        ignore = {"pts-cs75", "pts-cs1.10", "pts-cs7", "pts-cs8", "pts-cs12"}
        for verses in reference.index.values():  # type: ReferenceVerses
            if not verses.uid.key.raw.startswith("dn"):
                continue
            elif not verses.references.pts_cs:
                # No pts_cs reference in the reference list so skip it
                continue
            elif verses.references.pts_cs in ignore:
                continue
            if not verses.uid.key.seq.raw.startswith(verses.references.pts_cs.pts_no):
                log.error(
                    "[%s] wrong uid '%s' for pts_cs number: %s",
                    self.name,
                    verses.uid,
                    verses.references.pts_cs,
                )

    def get_missing_ms_id_from_reference(self, aggregate: YuttaAggregate):
        diff = sorted(
            {k for k in aggregate.index if k not in self.reference_engine.ms_id_index}
        )
        if diff:
            log.error(self._MS_REF_MISS_COUNT, self.__class__.__name__, len(diff))
            log.error(self._MS_REF_MISS, self.__class__.__name__, diff)
        return diff

    def log_wrong_ms_id_in_reference_data(self, aggregate: YuttaAggregate):
        diff = sorted(
            {k for k in self.reference_engine.ms_id_index if k not in aggregate.index}
        )
        if diff:
            log.error(self._MS_REF_MISS, self.__class__.__name__, len(diff))
            log.error(self._MS_WRONG, self.__class__.__name__, diff)

    def log_wrong_uid_in_reference_data(self, bilara: BilaraRootAggregate):
        diff = sorted(
            {k for k in self.reference_engine.uid_index if k not in bilara.index}
        )
        if diff:
            log.error(self._UID_WRONG_COUNT, self.__class__.__name__, len(diff))
            log.error(self._UID_WRONG, self.__class__.__name__, diff)

    @classmethod
    def get_wrong_segments_based_on_nya(cls, reference: BilaraReferenceAggregate):
        wrong_keys = set()
        for uid, ref_verses in reference.index.items():
            nya_id = ref_verses.references.nya
            if not nya_id:
                continue
            is_uid_ok = nya_id == f"nya{uid.key.seq[0]}"
            if not is_uid_ok:
                wrong_keys.add(uid)
        if wrong_keys:
            omg = "[RefEngine] There are '%s' nya ref not aligned with uid: %s"
            log.error(omg, len(wrong_keys), wrong_keys)
        return wrong_keys

    @property
    def name(self):
        return self.__class__.__name__
