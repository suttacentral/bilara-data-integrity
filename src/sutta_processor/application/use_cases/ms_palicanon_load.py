import logging

from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


def ms_palicanon_load(cfg: Config):
    log.info("Loading pali canon from: '%s'", cfg.pali_canon_path)
    root_aggregate = cfg.repo.get_all_pali_canon()
    log.info("Got root aggregate: %s", root_aggregate)
