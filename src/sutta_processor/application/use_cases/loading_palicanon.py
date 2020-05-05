import logging

from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


def loading_palicanon(cfg: Config):
    log.info("Loading files from: '%s'", cfg.pali_canon_path)
