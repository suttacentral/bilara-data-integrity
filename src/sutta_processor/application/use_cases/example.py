import logging

from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


def example(cfg: Config):
    log.info("Example log with cfg: %s", cfg)
