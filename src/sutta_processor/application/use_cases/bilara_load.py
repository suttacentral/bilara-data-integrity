import logging

from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


def bilara_load(cfg: Config):
    root_aggregate = cfg.repo.bilara.get_root()
    log.info("Got root aggregate: %s", root_aggregate)
