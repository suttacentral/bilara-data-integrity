import logging

from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


def ms_yuttadhammo_load(cfg: Config):
    root_aggregate = cfg.repo.get_ms_yuttadhammo()
    log.info("Got root aggregate: %s", root_aggregate)
