import logging

from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


def checking_uid(cfg: Config):
    sutta_mn = cfg.repo.get_example()
    log.info("sutta_mn: %s", sutta_mn)
