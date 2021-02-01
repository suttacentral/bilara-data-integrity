import logging
from collections import Counter, defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Set

from sutta_processor.application.domain_models import (
    BilaraRootAggregate,
    YuttaAggregate,
)
from sutta_processor.application.domain_models.base import BaseVerses
from sutta_processor.application.domain_models.ms_yuttadhammo.base import YuttaVerses
from sutta_processor.application.value_objects import (
    UID,
    BaseUID,
    MsId,
    RootUID,
    Verse,
    VerseTokens,
)
from sutta_processor.shared.exceptions import NoTokensError

from ..domain_models.bilara_root.root import Verses
from .base import ServiceBase
from .bd_reference import SCReferenceService
from .tokenizer import VersetTokenizer

log = logging.getLogger(__name__)


@dataclass
class RootUidTokens:
    uid: RootUID
    tokens: VerseTokens


class TextMatcher:
    # TODO: Check which ids were not matched in root
    # TODO: Check which ms_ids didn't found a match
    # TODO: Check which...

    roots_uid_tokens_index: Dict[RootUID, RootUidTokens]

    def __init__(self, root: BilaraRootAggregate, pali: YuttaAggregate):
        def get_unmatched_root_index() -> Dict[RootUID, RootUidTokens]:
            index_combined: Dict[RootUID, List[Verses]] = defaultdict(list)
            index_text_combined: Dict[RootUID, RootUidTokens] = {}
            for uid, verses in root.index.items():
                if 0 in uid.key.seq:
                    continue
                index_combined[uid.root].append(verses)

            for root_uid, verses_list in index_combined.items():
                try:
                    txt = " ".join((verses.verse for verses in verses_list))
                    tokens = VersetTokenizer.get_tokens(txt)
                    index_text_combined[root_uid] = RootUidTokens(root_uid, tokens)
                except NoTokensError as e:
                    log.error(e)
            return index_text_combined

        self.c: Counter = Counter(
            ok=0, error=0, all=0, missing_in_index=0, missing_in_reference=0
        )
        self.wrong_keys = set()
        self.root = root
        self.pali = pali

        self.roots_uid_tokens_index = get_unmatched_root_index()

    def get_missing_root_text_from_ms(self) -> set:

        for i, verses in enumerate(self.pali.index.values()):
            # ms_id, verses = item  # type: MsId, YuttaVerses
            # if "ms25Cn_738" not in uids:
            #     continue
            if i > 30:
                break
            try:
                self.process_yutta_verse(i=i, verses=verses)
            except Exception as e:
                log.exception(e)
        log.error("-" * 80)
        log.error("-" * 80)
        return self.wrong_keys

    def process_yutta_verse(self, i: int, verses: YuttaVerses):
        def get_ratio():
            ratio_map = {}
            matcher = SequenceMatcher()
            matcher.set_seq1(verses.verse.tokens)
            for root_tokens in self.roots_uid_tokens_index.values():
                matcher.set_seq2(root_tokens.tokens)
                ratio = matcher.quick_ratio()
                if ratio > 0.7:
                    omg = "Ratio for yt: '%s' root: '%s', ratio: %s"
                    log.error(omg, verses.ms_id, root_tokens.uid, ratio)
                    ratio_map[root_tokens.uid] = ratio
            if not ratio_map:
                omg = "Couldn't find a match ms_uid: '%s' tokes: %s"
                log.error(omg, verses.ms_id, verses.verse.tokens)
            return ratio_map

        self.ratios: Dict[MsId, Dict[RootUID, float]] = defaultdict(dict)
        self.c["all"] += 1
        try:
            self.ratios[verses.ms_id] = get_ratio()
        except Exception as e:
            log.exception(e)
            return
        self.c["ok"] += 1

    def print_summary(self):
        ratio = (self.c["error"] / self.c["all"]) * 100 if self.c["all"] else 0
        omg = "[%s] Found keys: '%s', errors: '%s' (ratio: %.2f%%), wrong_keys: %s"
        log.error(omg, self.name, self.c["ok"], self.c["error"], ratio, self.wrong_keys)
        # for i, ms_id in enumerate(self.wrong_keys):
        #     if i > 10:
        #         break
        #     self.print_verse_details(ms_id=ms_id, root=self.root, pali=self.pali)

    @property
    def name(self):
        return self.__class__.__name__


class CheckText(ServiceBase):
    reference: SCReferenceService

    def __init__(self, cfg):
        super().__init__(cfg=cfg)
        self.reference = SCReferenceService(cfg=cfg)

    def get_missing_text(
        self, root: BilaraRootAggregate, pali: YuttaAggregate
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

        for uid, verses in root.index.items():
            if is_skipped(uid) or is_key_missing(uid):
                continue

            c["all"] += 1
            ms_id = self.reference.reference_engine.uid_index[uid]
            root_tokens = verses.verse.tokens
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
                    verses.verse,
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

    def get_missing_root_text_from_ms(
        self, root: BilaraRootAggregate, pali: YuttaAggregate
    ):
        result = TextMatcher(root=root, pali=pali).get_missing_root_text_from_ms()
        return result

    def get_missing_text_ms_source(
        self, root: BilaraRootAggregate, pali: YuttaAggregate
    ) -> Set[UID]:
        wrong_keys = set()

        def get_root_verses(ms_id) -> Optional[BaseVerses]:
            root_ids: set = self.reference.reference_engine.ms_id_index.get(ms_id)
            if not root_ids:
                c["missing_in_reference"] += 1
                return None
            if len(root_ids) != 1:
                omg = f"MsId '{ms_id}' referencing more than one segment id:{root_ids}"
                raise RuntimeError(omg)
            root_vers: BaseVerses = root.index[root_ids.pop()]
            return root_vers

        c: Counter = Counter(
            ok=0, error=0, all=0, missing_in_index=0, missing_in_reference=0
        )
        for i, items in enumerate(pali.text_index.items()):
            tokens, uids = items
            # if "ms25Cn_738" not in uids:
            #     continue
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
                    root_verses = get_root_verses(ms_id=ms_id)
                    if root_verses and "EMPTY" in root_verses.verse.tokens.head_key:
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
        self, ms_id: MsId, root: BilaraRootAggregate, pali: YuttaAggregate,
    ):
        def print_details(uid_):
            root_vers: BaseVerses = root.index[uid_]
            log.error("Root verset: '%s'", root_vers.verse)
            log.error("Root tokens: '%s'", root_vers.verse.tokens.head_key)

        log.error(f"{'=' * 40} %s {'=' * 40}", ms_id)
        pali_vers: YuttaVerses = pali.index[ms_id]
        log.error("Pali verset: '%s'", pali_vers.verse)
        log.error("Pali tokens: '%s'", pali_vers.verse.tokens.head_key)

        try:
            root_ids: set = self.reference.reference_engine.ms_id_index[ms_id]
            for uid in root_ids:
                print_details(uid_=uid)
                log.error("-" * 40)
        except KeyError:
            log.error("Can't find reference for: '%s'", ms_id)

        log.error(f"{'=' * 40} %s {'=' * 40}", ms_id)
