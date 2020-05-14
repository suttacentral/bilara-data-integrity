import logging

from sutta_processor.application.domain_models import (
    BilaraHtmlAggregate,
    BilaraRootAggregate,
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
    _SURPLUS_UIDS = "[%s] There are '%s' UIDs that are not in the '%s' data"
    _SURPLUS_UIDS_LIST = "[%s] Surplus UIDs in the html: %s"

    def get_missing_segments(
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

    def get_surplus_segments(
        self, html_aggregate: BilaraHtmlAggregate, base_aggregate: BilaraRootAggregate
    ):
        base_uids = set(base_aggregate.index.keys())
        html_uids = set(html_aggregate.index.keys())
        html_surplus = html_uids - base_uids
        if html_surplus:
            log.error(
                self._SURPLUS_UIDS, self.name, len(html_surplus), base_aggregate.name()
            )
            log.error(self._SURPLUS_UIDS_LIST, self.name, sorted(html_surplus))


class CheckService(ServiceBase):
    def __init__(self, cfg: Config):
        super().__init__(cfg=cfg)
        self.reference = SCReferenceService(cfg=cfg)
        self.concordance = ConcordanceService(cfg=cfg)
        self.html = CheckHtml(cfg=cfg)

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
