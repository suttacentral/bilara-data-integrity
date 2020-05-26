import logging

from sutta_processor.application.check_service import CheckService
from sutta_processor.application.domain_models import BilaraRootAggregate
from sutta_processor.application.domain_models.ms_yuttadhammo.root import YuttaAggregate
from sutta_processor.infrastructure.repository.repo import FileRepository
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


# noinspection PyDataclass
def reference_data_check(cfg: Config):
    cfg.repo: FileRepository
    cfg.check: CheckService
    yutta_aggregate: YuttaAggregate = cfg.repo.yutta.get_aggregate()
    bilara_root: BilaraRootAggregate = cfg.repo.bilara.get_root()
    cfg.check.reference.get_missing_ms_id_from_reference(aggregate=yutta_aggregate)
    cfg.check.reference.log_wrong_ms_id_in_reference_data(aggregate=yutta_aggregate)
    cfg.check.reference.log_wrong_uid_in_reference_data(bilara=bilara_root)
