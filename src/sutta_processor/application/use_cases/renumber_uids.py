import logging

from sutta_processor.application.check_service import CheckService
from sutta_processor.application.domain_models import (
    BilaraReferenceAggregate,
    BilaraRootAggregate,
    ConcordanceAggregate,
)
from sutta_processor.infrastructure.repository.repo import FileRepository
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


# noinspection PyDataclass
def renumber_uids(cfg: Config):
    cfg.repo: FileRepository
    cfg.check: CheckService

    # yutta_aggregate: YuttaAggregate = cfg.repo.yutta.get_aggregate()
    reference: BilaraReferenceAggregate = cfg.repo.bilara.get_reference()
    # concordance: ConcordanceAggregate = cfg.repo.bilara.get_concordance()
    # cfg.check.reference.update_references_from_concordance(
    #     reference=reference, concordance=concordance
    # )
    # bilara: BilaraRootAggregate = cfg.repo.bilara.get_root()
    cfg.check.reference.get_wrong_segments_based_on_nya(reference=reference)
