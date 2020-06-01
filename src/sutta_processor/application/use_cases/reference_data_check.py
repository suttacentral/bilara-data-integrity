import logging

from sutta_processor.application.check_service import CheckService
from sutta_processor.application.domain_models import (
    BilaraReferenceAggregate,
    ConcordanceAggregate,
)
from sutta_processor.infrastructure.repository.repo import FileRepository
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


# noinspection PyDataclass
def reference_data_check(cfg: Config):
    cfg.repo: FileRepository
    cfg.check: CheckService

    def check_pts_cs_numbers():
        cfg.check.reference.get_wrong_pts_cs_no(reference=reference)

    # yutta_aggregate: YuttaAggregate = cfg.repo.yutta.get_aggregate()
    reference: BilaraReferenceAggregate = cfg.repo.bilara.get_reference()
    concordance: ConcordanceAggregate = cfg.repo.bilara.get_concordance()
    cfg.check.reference.update_references_from_concordance(
        reference=reference, concordance=concordance
    )
    cfg.repo.bilara.save(aggregate=reference)
    cfg.repo.bilara.save(aggregate=concordance)

    # cfg.check.save_csv_diff(bilara=bilara_root, bilara_begin=bilara_root_begin)
    # cfg.check.reference.get_missing_ms_id_from_reference(aggregate=yutta_aggregate)
    # cfg.check.reference.log_wrong_ms_id_in_reference_data(aggregate=yutta_aggregate)
    # cfg.check.reference.log_wrong_uid_in_reference_data(bilara=bilara_root)
