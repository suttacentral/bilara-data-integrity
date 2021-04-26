import logging

from sutta_processor.application.check_service import CheckService
from sutta_processor.application.domain_models import BilaraReferenceAggregate
from sutta_processor.infrastructure.repository.repo import FileRepository
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


# noinspection PyDataclass
def bilara_check_references(cfg: Config):
    cfg.repo: FileRepository
    cfg.check: CheckService
    reference: BilaraReferenceAggregate = cfg.repo.bilara.get_reference()
    cfg.check.reference.get_duplicated_ms_id(reference=reference)
    cfg.check.reference.get_wrong_segments_based_on_nya(reference=reference)
