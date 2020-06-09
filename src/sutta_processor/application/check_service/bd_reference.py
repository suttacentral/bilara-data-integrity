import json
import logging
import operator
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set
from functools import reduce

from sutta_processor.application.domain_models import (
    BilaraRootAggregate,
    PaliCanonAggregate,
    YuttaAggregate,
)
from sutta_processor.application.value_objects import UID, MsId
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
    _reference_engine: ReferenceEngine = None
    _MS_REF_MISS_COUNT = (
        "[%s] There are '%s' MsId that are not found in the reference file"
    )
    _MS_REF_MISS = "[%s] Missing MsId from reference: %s"
    _MS_WRONG_COUNT = "[%s] There are '%s' wrong MsId in the reference data"
    _MS_WRONG = "[%s] Wrong MsId is the reference data: %s"
    _UID_WRONG_COUNT = "[%s] There are '%s' wrong SC UID in the reference data"
    _UID_WRONG = "[%s] Wrong SC UID is the reference data: %s"
    _MS_REF_MATCH_COUNT = (
        "[%s] There are '%s' MsId that were found in both bilara data and in ms_yuttadhamo"
    )

    def __init__(self, cfg: Config):
        self.cfg = cfg

    def get_missing_ms_id_from_reference(self, aggregate: YuttaAggregate):
        diff = sorted(
            {k for k in aggregate.index if k not in self.reference_engine.ms_id_index}
        )
        match = sorted(
            {k for k in aggregate.index if k in self.reference_engine.ms_id_index}
        )
        if diff:
            log.error(self._MS_REF_MISS_COUNT, self.__class__.__name__, len(diff))
            log.error(self._MS_REF_MISS, self.__class__.__name__, diff)
        if match:
            log.error(self._MS_REF_MATCH_COUNT, self.__class__.__name__, len(match))
        return diff, match
    
    def validate_text_based_on_references(self, yutta_aggregate: YuttaAggregate, bilara_aggregate: BilaraRootAggregate):
        # CAVEAT: list that contains ms_ids that were found both in bilara-data and in ms_yuttadhamo
        match = sorted(
            {k for k in yutta_aggregate.index if k in self.reference_engine.ms_id_index}
        )
        # CAVEAT: extracting uids for matched ms_ids
        matched_uids = {ms_id: [uid] for uid, ms_id in self.reference_engine.uid_index.items() if ms_id in match}
        #log.error(f"Matched uids:\n{matched_uids}\n\n")
        log.error(f"UIDs that were correctly matched: {matched_uids.values()}")
        # TODO: check for gaps in between matched_uids
        set_matched_uids = set(reduce(operator.add, matched_uids.values()))
        log.error(f"Number of UIDS in matched_uids prior to  filling the gaps: {len(set_matched_uids)}")
        log.error(f"set_matched_uids: {set_matched_uids}")
        log.error(f"UIDS checked:")
        for ms_id, uid in matched_uids.items():
            # CAVEAT: since at this point uids have always one entry, I can just access the first element of uid here
            uid = uid[0]
            if '.' in uid:
                try:
                    uid_colon_separated = uid.split(':')
                    # CAVEAT: reversing the list at the point of its initialization; needs to be reversed back prior to
                    # any lookups in other data structures
                    original_subsections_numbers = uid_colon_separated[-1].split('.')[::-1]
                    # CAVEAT: implement counter how may elements after split('.') there is in a list and iterate over all of them
                    for i in range(len(original_subsections_numbers)):
                        initial_subsections_numbers = [x for x in original_subsections_numbers]
                        temp_subsections_numbers = initial_subsections_numbers
                        # FIXME: increment further numbers in the original subsections ONLY if for a given UID there are no further numbers:
                        # FIXME: mn26:33.1 should be checked ONLY if mn26:32.x search has exhausted the maximum number from 32 subsection
                        # TODO: get the maximum number for a given subsection from a list of valid UIDS
                        # mn26:32.2
                        #['2', '32']
                        while True:
                            # CAVEAT: if not the first subsection is checked, numbers in previous subsections are 1
                            if i > 0:
                                for j in range(i):
                                    temp_subsections_numbers[j] = '1'
                                log.error(f"temp_subsections_numbers: {temp_subsections_numbers}; initial_subsections_numbers : {initial_subsections_numbers}")
                            number_incremented = int(temp_subsections_numbers[i]) + 1
                            temp_subsections_numbers[i] = str(number_incremented)
                            # CAVEAT: reversing back numbers so they can be looked up
                            temp_subsections_numbers_reversed = temp_subsections_numbers[::-1]
                            uid_incremented = []
                            uid_incremented.append(uid_colon_separated[0])
                            uid_incremented.append('.'.join(temp_subsections_numbers_reversed))
                            uid_incremented = ':'.join(uid_incremented)
                            log.error(f"UID: {uid}; incremented_uid: {uid_incremented}")
                            if uid_incremented not in matched_uids[ms_id]:
                                log.error(f"{uid_incremented} not in matched_uid.keys()")
                                if uid_incremented not in set_matched_uids:
                                    log.error(f"{uid_incremented} not in set_matched_uids")
                                    if uid_incremented in bilara_aggregate.index.keys():
                                        set_matched_uids.add(uid_incremented)
                                        matched_uids[ms_id].append(uid_incremented)
                                        uid = uid_incremented
                                        log.error(f"Following uid was added to no_references_uids: {uid_incremented}")
                                    else:
                                        log.error(f"{uid_incremented} not in self.bilara_aggregate.index.keys()")
                                        break
                                else:
                                    break
                            else:
                                break
                        if i > len(original_subsections_numbers):
                            # TODO: check if there is any bigger number in a given subsection
                            # TODO: get the number for a given subsection from uid_incremented and check if it is equal or bigger than the
                            # TODO: biggest number in a current subsection
                            uid_incremented_colon_separated = uid.split(':')
                            temp_subsections_numbers = uid_incremented_colon_separated[-1].split('.')[::-1]
                            considered_number = temp_subsections_numbers[i]
                except Exception as e:
                    log.error(e)
            else:
                while True:
                    try:
                        last_element = str(int(uid.split(":")[-1]) + 1)
                        uid_incremented = last_element.join(uid.rsplit(uid.rsplit(':', 1)[-1], 1))
                        if uid_incremented not in matched_uids[ms_id]:
                            log.error(f"{uid_incremented} not in matched_uid.keys()")
                            if uid_incremented not in set_matched_uids:
                                log.error(f"{uid_incremented} not in set_matched_uids")
                                if uid_incremented in bilara_aggregate.index.keys():
                                    set_matched_uids.add(uid_incremented)
                                    matched_uids[ms_id].append(uid_incremented)
                                    uid = uid_incremented
                                    log.error(f"Following uid was added to no_references_uids: {uid_incremented}")
                                else:
                                    log.error(f"{uid_incremented} not in self.bilara_aggregate.index.keys()")
                                    break
                            else:
                                break
                        else:
                            break
                    except Exception as e:
                        log.error(f"No colon in uid and exception occured: {e}")
        # FIXME: count it realiably; currently it checks the amount of lists in lists
        log.error(f"Number of UIDS in matched_uids after filling the gaps: {len(matched_uids.values())}")


        # CAVEAT: Verses from bilara-data should be values in a dict, where keys are corresponding ms_ids
        bilara_verses = defaultdict(list)
        invalid_uids = []
        for ms_id, uid in matched_uids.items():
            log.error(f"{ms_id}: {uid}")
            try:
                for single_uid in uid:
                    bilara_verses[ms_id].append(bilara_aggregate.index[single_uid].verse)
            except Exception as e:
                # CAVEAT: if error happens it means that there were no verse for this uid
                invalid_uids.append(uid)
        if len(invalid_uids) > 0:
            log.error(f"There were {len(invalid_uids)} UIDs that were found in references but do not exist in bilara-data.")


        # CAVEAT: print Verses from ms yuttadhamo and bilara next to each other
        for id in match:
            try:
                log.error(f"\nPair for ms_id: {id}, UID: {matched_uids[id]}:")
                log.error(f"Yutta:\n{yutta_aggregate.index[id].verse}")
                log.error(f"Bilara:\n{bilara_verses[id]}")
            except Exception as e:
                 log.error(e)
        

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

    def get_wrong_segments_based_on_nya(self, bilara: BilaraRootAggregate):
        wrong_keys = set()
        for uid in bilara.index.keys():
            if not uid.startswith("mn") or uid.startswith("mnd"):
                continue
            idx = uid.key.seq[0]
            reference: str = self.reference_engine.uid_reference.get(uid, set())
            is_to_check = uid.key.seq[-1] == 1 or "nya" in str(reference)
            if 0 in uid.key.seq or not is_to_check:
                continue
            expected_ref = f"nya{idx}"

            if expected_ref not in reference:
                omg = "[RefEngine] uid '%s' not found in reference: '%s'"
                log.error(omg, uid, reference)
                wrong_keys.add(uid)
        if wrong_keys:
            omg = "[RefEngine] There are '%s' mn keys not in reference"
            log.error(omg, len(wrong_keys))
        return wrong_keys

    @property
    def reference_engine(self) -> ReferenceEngine:
        if not self._reference_engine:
            self._reference_engine = ReferenceEngine(cfg=self.cfg)
        return self._reference_engine
