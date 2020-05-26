import logging
from collections import Counter
from dataclasses import dataclass
from typing import List, Optional, Set

from sutta_processor.application.domain_models import (
    BilaraRootAggregate,
    YuttaAggregate,
)
from sutta_processor.application.domain_models.base import BaseVersus
from sutta_processor.application.domain_models.ms_yuttadhammo.base import YuttaVersus
from sutta_processor.application.value_objects import UID, BaseUID, MsId, VerseTokens

from ...shared.exceptions import NoTokensError
from .base import ServiceBase
from .bd_reference import SCReferenceService

log = logging.getLogger(__name__)


@dataclass
class KeyToken:
    uid: BaseUID
    token: str


class TextMatcher:
    # TODO: Check which ids were not matched in root
    # TODO: Check which ms_ids didn't found a match
    # TODO: Check which...
    def __init__(self, root: BilaraRootAggregate, pali: YuttaAggregate):
        def get_unmatched_root_index() -> List[KeyToken]:
            unmatched_index = []
            for uid, versus in root.index.items():
                try:
                    for token in versus.verse.tokens:
                        unmatched_index.append(KeyToken(uid, token))
                except NoTokensError:
                    pass
            return unmatched_index

        self.c: Counter = Counter(
            ok=0, error=0, all=0, missing_in_index=0, missing_in_reference=0
        )
        self.wrong_keys = set()
        self.root = root
        self.pali = pali

        self.unmatched_index: List[KeyToken] = get_unmatched_root_index()

    def get_missing_root_text_from_ms(self) -> set:

        for i, items in enumerate(self.pali.text_index.items()):
            tokens, ms_ids = items
            # if "ms25Cn_738" not in uids:
            #     continue
            try:
                self.process_yutta_verse(i=i, yutta_verse_tokens=tokens, ms_ids=ms_ids)
            except Exception as e:
                log.exception(e)
        return self.wrong_keys

    def process_yutta_verse(
        self, i: int, yutta_verse_tokens: VerseTokens, ms_ids: Set[MsId]
    ):
        def get_starting_match_index():
            yutta_idx = 0
            yutta_len = len(yutta_verse_tokens)
            for i, key_token in enumerate(self.unmatched_index):
                if key_token.token == yutta_verse_tokens[yutta_idx]:
                    if yutta_idx == 2:
                        print(key_token.token)
                        print("yutta tokens:", yutta_verse_tokens)
                        print("root tokens:", self.unmatched_index[i : i + yutta_len])
                        print()
                    yutta_idx += 1
                    if yutta_idx == yutta_len:
                        return i
                yutta_idx = 0
            else:
                raise RuntimeError("No tokens match found")

        self.c["all"] += 1
        try:
            start_idx = get_starting_match_index()
            end_idx = len(yutta_verse_tokens)
            log.error("Token match found! %s, %s", start_idx, yutta_verse_tokens)
            self.unmatched_index[start_idx:end_idx] = []
        except Exception:
            # log.exception(e)
            return
        self.c["ok"] += 1

    def handle_missing(self):
        ...

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

    def get_missing_root_text_from_ms(
        self, root: BilaraRootAggregate, pali: YuttaAggregate
    ):
        result = TextMatcher(root=root, pali=pali).get_missing_root_text_from_ms()
        return result

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
        self, ms_id: MsId, root: BilaraRootAggregate, pali: YuttaAggregate,
    ):
        def print_details(uid_):
            root_vers: BaseVersus = root.index[uid_]
            log.error("Root verset: '%s'", root_vers.verse)
            log.error("Root tokens: '%s'", root_vers.verse.tokens.head_key)

        log.error(f"{'=' * 40} %s {'=' * 40}", ms_id)
        pali_vers: YuttaVersus = pali.index[ms_id]
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
