import logging

from sutta_processor.application.domain_models import (
    BilaraCommentAggregate,
    BilaraHtmlAggregate,
    BilaraRootAggregate,
    BilaraTranslationAggregate,
)
from sutta_processor.application.value_objects.uid import UidKey
from sutta_processor.shared.config import Config

from ..domain_models.base import BaseRootAggregate
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

    def log_missing_segments(
        self, html_aggregate: BilaraHtmlAggregate, base_aggregate: BaseRootAggregate
    ):
        base_uids = set(base_aggregate.index.keys())
        html_uids = set(html_aggregate.index.keys())
        html_missing = base_uids - html_uids
        if html_missing:
            log.error(
                self._MISSING_UIDS, self.name, len(html_missing), base_aggregate.name()
            )
            log.error(self._MISSING_UIDS_LIST, self.name, sorted(html_missing))

    def log_surplus_segments(
        self, check_aggregate: BilaraHtmlAggregate, base_aggregate: BaseRootAggregate,
    ):
        base_uids = set(base_aggregate.index.keys())
        html_uids = set(check_aggregate.index.keys())
        html_surplus = html_uids - base_uids
        # Headings that were added to the translation.
        # Filter out headings by removing all entries ending with 0.
        html_wrong = set(uid for uid in html_surplus if 0 not in uid.key.seq)
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


class CheckTranslation(ServiceBase):
    _SURPLUS_UIDS = (
        "[%s] There are '%s' UIDs in '%s' lang that are not in the '%s' data"
    )
    _SURPLUS_UIDS_LIST = "[%s] Surplus UIDs in the '%s' lang: %s"

    def log_surplus_segments(
        self,
        translation_aggregate: BilaraTranslationAggregate,
        base_aggregate: BaseRootAggregate,
    ):
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


class CheckService(ServiceBase):
    _SURPLUS_UIDS = "[%s] There are '%s' uids in '%s' that are not in the '%s' data"
    _SURPLUS_UIDS_LIST = "[%s] Surplus '%s' UIDs: %s"

    def __init__(self, cfg: Config):
        super().__init__(cfg=cfg)
        self.reference = SCReferenceService(cfg=cfg)
        self.concordance = ConcordanceService(cfg=cfg)
        self.html = CheckHtml(cfg=cfg)
        self.translation = CheckTranslation(cfg=cfg)

    def log_surplus_segments(
        self, check_aggregate: BaseRootAggregate, base_aggregate: BaseRootAggregate,
    ):
        cb_mapping = {
            BilaraTranslationAggregate: self.translation.log_surplus_segments,
            BilaraHtmlAggregate: self.html.log_surplus_segments,
        }
        callback = cb_mapping.get(type(check_aggregate), self._log_surplus_segments)
        callback(check_aggregate, base_aggregate=base_aggregate)

    def _log_surplus_segments(
        self, check_aggregate: BaseRootAggregate, base_aggregate: BaseRootAggregate,
    ):
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

    def check_uid_sequence_in_file(self, aggregate: BilaraRootAggregate):
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
