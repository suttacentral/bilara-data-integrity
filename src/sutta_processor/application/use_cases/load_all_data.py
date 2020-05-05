import logging

from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


def load_all_data(cfg: Config):
    root_aggregate = cfg.repo.get_all_sutta_central()
    log.info("Got root aggregate: %s", root_aggregate)
