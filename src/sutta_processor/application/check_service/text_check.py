import logging
from collections import Counter
from typing import Optional, Set

from sutta_processor.application.domain_models import (
    BilaraRootAggregate,
    YuttaAggregate,
)
from sutta_processor.application.domain_models.base import BaseVersus
from sutta_processor.application.domain_models.ms_yuttadhammo.base import YuttaVersus
from sutta_processor.application.value_objects import UID, MsId

from .base import ServiceBase
from .bd_reference import SCReferenceService

log = logging.getLogger(__name__)


class TextMatcher(ServiceBase):
    pass


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
