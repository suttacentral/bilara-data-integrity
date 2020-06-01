import logging

from sutta_processor.application.check_service import CheckService
from sutta_processor.application.domain_models import BilaraRootAggregate
from sutta_processor.infrastructure.repository.repo import FileRepository
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


# noinspection PyDataclass
def bilara_load(cfg: Config):
    cfg.repo: FileRepository
    cfg.check: CheckService
    root_aggregate: BilaraRootAggregate = cfg.repo.bilara.get_root()
    log.info("Got root aggregate: %s", root_aggregate)
