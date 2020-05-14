import logging

from sutta_processor.application.domain_models import BilaraRootAggregate
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


def bilara_check_segments(cfg: Config):
    root_aggregate: BilaraRootAggregate = cfg.repo.bilara.get_root()
    cfg.bdata_check.check_uid_sequence_in_file(aggregate=root_aggregate)
