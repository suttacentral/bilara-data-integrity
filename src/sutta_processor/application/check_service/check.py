import logging

from sutta_processor.application.domain_models import BilaraRootAggregate
from sutta_processor.application.value_objects.uid import UidKey
from sutta_processor.shared.config import Config

from .bd_reference import SCReferenceService
from .concordance import ConcordanceService

log = logging.getLogger(__name__)


class CheckService:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.reference = SCReferenceService(cfg=cfg)
        self.concordance = ConcordanceService(cfg=cfg)

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
