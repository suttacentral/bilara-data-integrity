import logging

from sutta_processor.application.domain_models.pali_canon.root import PaliCanonAggregate
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


def check_reference_data(cfg: Config):
    pali_aggregate: PaliCanonAggregate = cfg.repo.get_all_pali_canon()
    cfg.sc_reference.log_missing_pali_id_from_reference(pali_aggregate=pali_aggregate)
    cfg.sc_reference.log_wrong_ids_in_reference_data(pali_aggregate=pali_aggregate)
