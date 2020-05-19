import logging
import re

from sutta_processor.application.domain_models import (
    BilaraHtmlAggregate,
    BilaraRootAggregate,
    BilaraTranslationAggregate,
)
from sutta_processor.application.domain_models.base import BaseRootAggregate, BaseVersus
from sutta_processor.application.value_objects.uid import UID, UidKey
from sutta_processor.shared.config import Config
from sutta_processor.shared.false_positives import DUPLICATE_OK_IDS, HTML_CHECK_OK_IDS

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
        self, check_aggregate: BilaraHtmlAggregate, base_aggregate: BaseRootAggregate,
    ) -> set:
        base_uids = set(base_aggregate.index.keys())
        html_uids = set(check_aggregate.index.keys())
        html_surplus = html_uids - base_uids

        def is_ignored(uid: UID) -> bool:
            """
            Headings that were added to the translation.
            Filter out headings by removing all entries ending with 0.
            """
            is_added_heading = 0 not in uid.key.seq
            return not is_added_heading or uid in self._ignored

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


class CheckTranslation(ServiceBase):
    _SURPLUS_UIDS = (
        "[%s] There are '%s' UIDs in '%s' lang that are not in the '%s' data"
    )
    _SURPLUS_UIDS_LIST = "[%s] Surplus UIDs in the '%s' lang: %s"

    def get_surplus_segments(
        self,
        translation_aggregate: BilaraTranslationAggregate,
        base_aggregate: BaseRootAggregate,
    ) -> set:
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


class CheckService(ServiceBase):
    _SURPLUS_UIDS = "[%s] There are '%s' uids in '%s' that are not in the '%s' data"
    _SURPLUS_UIDS_LIST = "[%s] Surplus '%s' UIDs: %s"

    def __init__(self, cfg: Config):
        super().__init__(cfg=cfg)
        self.reference = SCReferenceService(cfg=cfg)
        self.concordance = ConcordanceService(cfg=cfg)
        self.html = CheckHtml(cfg=cfg)
        self.translation = CheckTranslation(cfg=cfg)

    def get_surplus_segments(
        self, check_aggregate: BaseRootAggregate, base_aggregate: BaseRootAggregate,
    ) -> set:
        cb_mapping = {
            BilaraTranslationAggregate: self.translation.get_surplus_segments,
            BilaraHtmlAggregate: self.html.get_surplus_segments,
        }
        callback = cb_mapping.get(type(check_aggregate), self._get_surplus_segments)
        result = callback(check_aggregate, base_aggregate=base_aggregate)
        return result

    def _get_surplus_segments(
        self, check_aggregate: BaseRootAggregate, base_aggregate: BaseRootAggregate,
    ) -> set:
        base_uids = set(base_aggregate.index.keys())
        comm_uids = set(check_aggregate.index.keys())
        comm_surplus = comm_uids - base_uids
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
        previous_elem = UidKey(":")
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
        pattern = r"(\(\s\)|^\s$|^$)"
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
