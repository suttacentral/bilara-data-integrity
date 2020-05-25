import logging
import pprint
import re
from collections import Counter
from itertools import zip_longest
from typing import Dict, Optional, Set

from sutta_processor.application.domain_models import (
    BilaraHtmlAggregate,
    BilaraRootAggregate,
    BilaraTranslationAggregate,
    BilaraVariantAggregate,
    PaliCanonAggregate,
    YuttaAggregate,
)
from sutta_processor.application.domain_models.base import BaseRootAggregate, BaseVersus
from sutta_processor.application.value_objects.uid import UID, MsId, UidKey
from sutta_processor.shared.config import Config
from sutta_processor.shared.false_positives import (
    DUPLICATE_OK_IDS,
    HTML_CHECK_OK_IDS,
    HTML_START_HEADER_OK,
    VARIANT_ARROW_OK_IDS,
    VARIANT_UNKNOWN_OK_IDS,
)

from ..domain_models.ms_palicanon.base import PaliVersus
from .bd_reference import SCReferenceService
from .concordance import ConcordanceService

log = logging.getLogger(__name__)


class ServiceBase:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    @property
    def name(self) -> str:
        return self.__class__.__name__


class CheckHtml(ServiceBase):
    _MISSING_UIDS = "[%s] There are '%s' UIDs that are in '%s' but missing in the html"
    _MISSING_UIDS_LIST = "[%s] Missing UIDs from html: %s"
    _SURPLUS_UIDS = "[%s] There are '%s' uids in '%s' that are not in the '%s' data"
    _SURPLUS_UIDS_LIST = "[%s] Surplus '%s' UIDs: %s"

    _ignored = HTML_CHECK_OK_IDS

    def get_missing_segments(
        self, html_aggregate: BilaraHtmlAggregate, base_aggregate: BaseRootAggregate
    ) -> set:
        base_uids = set(base_aggregate.index.keys())
        html_uids = set(html_aggregate.index.keys())
        html_missing = base_uids - html_uids
        if html_missing:
            log.error(
                self._MISSING_UIDS, self.name, len(html_missing), base_aggregate.name()
            )
            log.error(self._MISSING_UIDS_LIST, self.name, sorted(html_missing))
        return html_missing

    def get_surplus_segments(
        self,
        check_aggregate: BilaraHtmlAggregate,
        base_aggregate: BaseRootAggregate,
        false_positive: Set[str] = None,
    ) -> set:
        false_positive = false_positive or {}
        base_uids = set(base_aggregate.index.keys())
        html_uids = set(check_aggregate.index.keys())
        html_surplus = html_uids - base_uids

        def is_ignored(uid: UID) -> bool:
            """
            Headings that were added to the translation.
            Filter out headings by removing all entries ending with 0.
            """
            is_added_heading = 0 not in uid.key.seq
            return not is_added_heading or uid in self._ignored.union(false_positive)

        html_wrong = sorted(uid for uid in html_surplus if not is_ignored(uid=uid))
        if html_wrong:
            log.error(
                self._SURPLUS_UIDS,
                self.name,
                len(html_wrong),
                check_aggregate.name(),
                base_aggregate.name(),
            )
            log.error(
                self._SURPLUS_UIDS_LIST,
                self.name,
                check_aggregate.name(),
                sorted(html_wrong),
            )
        return set(html_wrong)

    def is_0_in_header_uid(self, aggregate: BilaraHtmlAggregate) -> Set[UID]:
        error_uids = set()
        prog = re.compile(r"<h\d")
        for uid, versus in aggregate.index.items():
            if uid in HTML_START_HEADER_OK:
                continue
            elif prog.match(versus.verse) and 0 not in uid.key.seq:
                omg = "[%s] Possible header not starting the section: '%s'"
                log.error(omg, self.name, {uid: versus.verse})
                error_uids.add(uid)
        if error_uids:
            omg = "[%s] There are '%s' headers that don't start new section: %s"
            log.error(omg, self.name, len(error_uids), error_uids)
        return error_uids


class CheckTranslation(ServiceBase):
    _SURPLUS_UIDS = (
        "[%s] There are '%s' UIDs in '%s' lang that are not in the '%s' data"
    )
    _SURPLUS_UIDS_LIST = "[%s] Surplus UIDs in the '%s' lang: %s"

    def get_surplus_segments(
        self,
        translation_aggregate: BilaraTranslationAggregate,
        base_aggregate: BaseRootAggregate,
        false_positive: Set[str] = None,
    ) -> set:
        false_positive = false_positive or {}
        base_uids = set(base_aggregate.index.keys())
        for lang, lang_index in translation_aggregate.index.items():
            tran_uids = set(lang_index.keys())
            tran_surplus = tran_uids - base_uids
            if tran_surplus:
                log.error(
                    self._SURPLUS_UIDS,
                    self.name,
                    len(tran_surplus),
                    lang,
                    base_aggregate.name(),
                )
                log.error(
                    self._SURPLUS_UIDS_LIST, self.name, lang, sorted(tran_surplus)
                )
        return base_uids


class CheckVariant(ServiceBase):
    _MISSING_WORD = "[%s] Word '%s' not found in the base verse: '%s'"
    _MISSING_KEY = "[%s] Key '%s' was not found in '%s'"

    def get_wrong_uid_with_arrow(
        self, aggregate: BilaraVariantAggregate, base_aggregate: BaseRootAggregate,
    ) -> Set[UID]:
        missing_word_keys = set()

        for uid, versus in aggregate.index.items():
            word, *rest = versus.verse.split("→")
            if not rest:
                continue
            word = word.strip()
            try:
                base_verse: str = base_aggregate.index[uid].verse
            except KeyError:
                log.error(self._MISSING_KEY, self.name, uid, base_aggregate.name())
                missing_word_keys.add(uid)
                continue

            if (word not in base_verse) and (uid not in VARIANT_ARROW_OK_IDS):
                log.error(self._MISSING_WORD, self.name, word, {uid: base_verse})
                missing_word_keys.add(uid)

        if missing_word_keys:
            omg = "[%s] Wrong word count: '%s' uids: '%s'"
            log.error(omg, self.name, len(missing_word_keys), missing_word_keys)
        return missing_word_keys

    def get_unknown_variants(self, aggregate: BilaraVariantAggregate) -> Set[UID]:
        unknown_keys = set()
        for uid, versus in aggregate.index.items():
            word, *rest = versus.verse.split("→")
            if rest or uid in VARIANT_UNKNOWN_OK_IDS:
                continue
            unknown_keys.add(uid)

        if unknown_keys:
            msg = "[%s] There are '%s' uids are not validated"
            log.error(msg, self.name, len(unknown_keys))
            values = {k: aggregate.index[k].verse for k in unknown_keys}
            pretty_values = pprint.pformat(values, width=200)
            log.error("[%s] Not valid keys: \n%s", self.name, pretty_values)
        return unknown_keys


class CheckText(ServiceBase):
    reference: SCReferenceService

    def __init__(self, cfg):
        super().__init__(cfg=cfg)
        self.reference = SCReferenceService(cfg=cfg)

    def get_missing_text(
        self, root: BilaraRootAggregate, pali: PaliCanonAggregate
    ) -> Set[UID]:
        wrong_keys = set()
        missing_reference_uids = set()
        missing_sources_ms_id = set()

        c: Counter = Counter(ok=0, error=0, all=0)

        def is_header(uid_: UID):
            return 0 in uid_.key.seq

        def is_skipped(uid_: UID) -> bool:
            is_right_text = uid_.startswith("mn10")
            skip_uid = {"ds1.2:200.33"}
            return not is_right_text or is_header(uid_) or uid_ in skip_uid

        def is_key_missing(uid_: UID) -> bool:
            try:
                ms_id_ = self.reference.reference_engine.uid_index[uid_]
            except KeyError:
                missing_reference_uids.add(uid_)
                return True
            try:
                pali.index[ms_id_]
            except KeyError:
                missing_sources_ms_id.add(ms_id_)
                return True
            return False

        for uid, versus in root.index.items():
            if is_skipped(uid) or is_key_missing(uid):
                continue

            c["all"] += 1
            ms_id = self.reference.reference_engine.uid_index[uid]
            root_tokens = versus.verse.tokens
            pali_tokens = pali.index[ms_id].verse.tokens
            if root_tokens != pali_tokens:
                omg = (
                    "[%s] Text mismatch for [%s]: root [%s], "
                    "source: [%s], token_root: [%s], token_source: [%s]"
                )
                log.error(
                    omg,
                    self.name,
                    uid,
                    versus.verse,
                    pali.index[ms_id].verse,
                    root_tokens,
                    pali_tokens,
                )
                c["error"] += 1
                wrong_keys.add(uid)
            c["ok"] += 1
        if wrong_keys:
            ratio = (c["error"] / c["all"]) * 100 if c["all"] else 0
            omg = "[%s] Good lines: '%s', errors: '%s' (ratio: %.2f%%), wrong_keys: %s"
            log.error(omg, self.name, c["ok"], c["error"], ratio, sorted(wrong_keys))
        if missing_reference_uids:
            omg = (
                "[%s] There are '%s' uids which don't have ms_id in the reference. "
                "processed ids: '%s' "
                "uids: %s"
            )
            log.error(
                omg,
                self.name,
                len(missing_reference_uids),
                c["all"],
                sorted(missing_reference_uids),
            )
        if missing_sources_ms_id:
            omg = "[%s] There are '%s' ms_id missing from source data. ms_ids: %s"
            log.error(
                omg, self.name, len(missing_sources_ms_id), missing_sources_ms_id,
            )
        return wrong_keys

    def get_missing_text_ms_source(
        self, root: BilaraRootAggregate, pali: YuttaAggregate
    ) -> Set[UID]:
        wrong_keys = set()

        def get_root_versus(ms_id) -> Optional[BaseVersus]:
            root_ids: set = self.reference.reference_engine.ms_id_index.get(ms_id)
            if not root_ids:
                c["missing_in_reference"] += 1
                return None
            if len(root_ids) != 1:
                omg = f"MsId '{ms_id}' referencing more than one segment id:{root_ids}"
                raise RuntimeError(omg)
            root_vers: BaseVersus = root.index[root_ids.pop()]
            return root_vers

        c: Counter = Counter(
            ok=0, error=0, all=0, missing_in_index=0, missing_in_reference=0
        )
        for i, items in enumerate(pali.text_index.items()):
            tokens, uids = items
            if "ms25Cn_738" not in uids:
                continue
            c["all"] += 1
            try:
                root.text_head_index[tokens.head_key]
            except KeyError:
                # TODO: Handle empty tokens (check loading)
                if "EMPTY" in tokens.head_key:
                    c["all"] -= 1
                    continue

                # TODO: Make multi id compilant
                ms_id = uids.pop()
                try:
                    root_versus = get_root_versus(ms_id=ms_id)
                    if root_versus and "EMPTY" in root_versus.verse.tokens.head_key:
                        # TODO: Handle empty tokens (do more validation with that)
                        c["all"] -= 1
                        continue
                except KeyError:
                    c["missing_in_index"] += 1
                    c["all"] -= 1
                    continue
                c["error"] += 1
                wrong_keys.update(uids)
                continue
            c["ok"] += 1

        ratio = (c["error"] / c["all"]) * 100 if c["all"] else 0
        omg = "[%s] Found keys: '%s', errors: '%s' (ratio: %.2f%%), wrong_keys: %s"
        log.error(omg, self.name, c["ok"], c["error"], ratio, wrong_keys)
        for i, ms_id in enumerate(wrong_keys):
            if i > 10:
                break
            self.print_verse_details(ms_id=ms_id, root=root, pali=pali)
        return wrong_keys

    def print_verse_details(
        self, ms_id: MsId, root: BilaraRootAggregate, pali: PaliCanonAggregate,
    ):
        def print_details(uid_):
            root_vers: BaseVersus = root.index[uid_]
            log.error("Root verset: '%s'", root_vers.verse)
            log.error("Root tokens: '%s'", root_vers.verse.tokens.head_key)

        log.error(f"{'='*40} %s {'='*40}", ms_id)
        pali_vers: PaliVersus = pali.index[ms_id]
        log.error("Pali verset: '%s'", pali_vers.verse)
        log.error("Pali tokens: '%s'", pali_vers.verse.tokens.head_key)

        try:
            root_ids: set = self.reference.reference_engine.ms_id_index[ms_id]
            for uid in root_ids:
                print_details(uid_=uid)
                log.error("-" * 40)
        except KeyError:
            log.error("Can't find reference for: '%s'", ms_id)

        log.error(f"{'='*40} %s {'='*40}", ms_id)


class CheckService(ServiceBase):
    _SURPLUS_UIDS = "[%s] There are '%s' uids in '%s' that are not in the '%s' data"
    _SURPLUS_UIDS_LIST = "[%s] Surplus '%s' UIDs: %s"

    def __init__(self, cfg: Config):
        super().__init__(cfg=cfg)
        self.reference = SCReferenceService(cfg=cfg)
        self.concordance = ConcordanceService(cfg=cfg)
        self.html = CheckHtml(cfg=cfg)
        self.translation = CheckTranslation(cfg=cfg)
        self.variant = CheckVariant(cfg=cfg)
        self.text = CheckText(cfg=cfg)
        self.sequence = SequenceCheck(cfg=cfg)

    def get_surplus_segments(
        self,
        check_aggregate: BaseRootAggregate,
        base_aggregate: BaseRootAggregate,
        false_positive: Set[str] = None,
    ) -> set:
        false_positive = false_positive or {}
        cb_mapping = {
            BilaraTranslationAggregate: self.translation.get_surplus_segments,
            BilaraHtmlAggregate: self.html.get_surplus_segments,
        }
        callback = cb_mapping.get(type(check_aggregate), self._get_surplus_segments)
        result = callback(
            check_aggregate,
            base_aggregate=base_aggregate,
            false_positive=false_positive,
        )
        return result

    def _get_surplus_segments(
        self,
        check_aggregate: BaseRootAggregate,
        base_aggregate: BaseRootAggregate,
        false_positive: Set[str],
    ) -> set:
        base_uids = set(base_aggregate.index.keys())
        comm_uids = set(check_aggregate.index.keys())
        comm_surplus = comm_uids - base_uids.union(false_positive)
        if comm_surplus:
            log.error(
                self._SURPLUS_UIDS,
                self.name,
                len(comm_surplus),
                check_aggregate.name(),
                base_aggregate.name(),
            )
            log.error(
                self._SURPLUS_UIDS_LIST,
                self.name,
                check_aggregate.name(),
                sorted(comm_surplus),
            )
        return comm_surplus

    def check_uid_sequence_in_file(self, aggregate: BilaraRootAggregate):
        error_keys = set()
        previous_elem = UidKey(":0-0")
        for uid in aggregate.index:
            if not uid.key.is_next(previous=previous_elem):
                error_keys.add(uid)
                msg = "[%s] Sequence error. Previous: '%s' current: '%s'"
                log.error(msg, self.name, previous_elem.raw, uid)
            previous_elem = uid.key
        if error_keys:
            msg = "[%s] There are '%s' sequence key errors"
            log.error(msg, self.name, len(error_keys))

    def get_duplicated_versus_next_to_each_other(
        self, aggregate: BilaraRootAggregate
    ) -> set:
        error_keys = set()
        prev_versus = ""
        for uid, versus in aggregate.index.items():  # type: UID, BaseVersus
            verse = versus.verse.strip()
            if not verse:
                continue
            if verse == prev_versus and uid not in DUPLICATE_OK_IDS:
                error_keys.add(uid)
                msg = "[%s] Same versus next to each other. '%s': '%s'"
                log.error(msg, self.name, uid, verse)
            prev_versus = verse
        if error_keys:
            msg = "[%s] There are '%s' duplicated versus error"
            log.error(msg, self.name, len(error_keys))
            msg = "[%s] dupes UIDs: %s"
            log.error(msg, self.name, sorted(error_keys))
        return error_keys

    def get_empty_verses(self, aggregate: BilaraRootAggregate) -> set:
        error_keys = set()
        pattern = r"(\(\s\)|^\s$)"
        prog = re.compile(pattern)
        for uid, versus in aggregate.index.items():  # type: UID, BaseVersus
            result = prog.match(versus.verse)
            if result:
                error_keys.add(uid)
                msg = "[%s] Key has blank value: '%s': '%s'"
                log.error(msg, self.name, uid, versus.verse)

        if error_keys:
            msg = "[%s] There are '%s' blank versus error"
            log.error(msg, self.name, len(error_keys))
            msg = "[%s] blank UIDs: %s"
            log.error(msg, self.name, sorted(error_keys))
        return error_keys

    def get_unordered_segments(
        self, aggregate: BaseRootAggregate, false_positive: Set[str] = None
    ):
        if isinstance(aggregate, BilaraTranslationAggregate):
            wrong_uids = set()
            for lang, lang_index in aggregate.index.items():
                unordered_seg = self.sequence.get_unordered_segments(index=lang_index)

                if unordered_seg:
                    omg = "[%s] There are '%s' unordered segments for lang: '%s'"
                    log.error(omg, self.name, len(unordered_seg), lang)
                wrong_uids.update(unordered_seg)
            return wrong_uids

        unordered_seg = self.sequence.get_unordered_segments(index=aggregate.index)
        if unordered_seg:
            omg = "[%s] There are '%s' unordered segments: %s"
            log.error(omg, self.name, len(unordered_seg), sorted(unordered_seg))
        return unordered_seg


class SequenceCheck(ServiceBase):
    def get_unordered_segments(self, index: Dict[UID, BaseVersus]) -> Set[UID]:
        wrong_uid = set()
        previous = UidKey(":0-0")
        for uid in index:
            current = uid.key
            if not self.is_key_in_seq(previous, current):
                omg = "[%s] Sequence error. Previous: '%s' current: '%s"
                log.error(omg, self.name, previous.raw, current.raw)
                wrong_uid.add(uid)
            previous = uid.key
        return wrong_uid

    @classmethod
    def is_key_in_seq(cls, previous: UidKey, current: UidKey) -> bool:
        def is_new_file():
            """ Reset sequence when new file. """
            return current.key != previous.key

        def is_same_level():
            return len(current.seq) == len(previous.seq)

        def is_last_gt():
            return current.seq.last > previous.seq.last

        def is_last_lt():
            """When jumping to next, shorter, block."""
            return current.seq.last < previous.seq.last

        def is_second_last_1gt():
            try:
                return current.seq.second_last == previous.seq.second_last + 1
            except ValueError:
                return False

        def is_level_lt():
            return len(current.seq) < len(previous.seq)

        def is_seq_gt():
            for we, them in zip_longest(current.seq, previous.seq):
                try:
                    if we > them:
                        return True
                except TypeError:
                    # Some are baked: '7-8' and they stay in str
                    return False
            return False

        def is_str_head_in_sequence():
            """ Resolve:
            previous: 'mn13:23-28.6' current: 'mn13:29.1'
            Previous: 'mn13:32.5' current: 'mn13:33-35.1'
            Previous: 'mn28:33-34.1' current: 'mn28:35-36.1'
            """
            current_sequence_number = current.seq.head
            previous_sequence_number = previous.seq.head
            if isinstance(current_sequence_number, str):
                current_sequence_number = int(current_sequence_number.split("-")[0])
            if isinstance(previous_sequence_number, str):
                previous_sequence_number = int(previous_sequence_number.split("-")[-1])
            return current_sequence_number == previous_sequence_number + 1

        if is_new_file():
            return True
        elif is_same_level():
            if is_last_gt():
                return True
            if is_second_last_1gt():
                return True
            if is_seq_gt():
                return True
        else:
            if is_seq_gt():
                return True
            if is_level_lt() and is_last_lt():
                # sequence should be shorter and start from 0,1
                return True
        return is_str_head_in_sequence()
