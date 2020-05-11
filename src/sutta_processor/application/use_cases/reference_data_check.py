import logging

from sutta_processor.application.domain_models import SuttaCentralAggregate
from sutta_processor.application.domain_models.ms_yuttadhammo.root import YuttaAggregate
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


def reference_data_check(cfg: Config):
    yutta_aggregate: YuttaAggregate = cfg.repo.yutta.get_aggregate()
    sutta_aggregate: SuttaCentralAggregate = cfg.repo.get_all_sutta_central()
    cfg.sc_reference.log_missing_ms_id_from_reference(pali_aggregate=yutta_aggregate)
    cfg.sc_reference.log_wrong_ms_id_in_reference_data(pali_aggregate=yutta_aggregate)
    cfg.sc_reference.log_wrong_uid_in_reference_data(sutta_aggregate=sutta_aggregate)
