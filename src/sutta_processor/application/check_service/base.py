import logging

from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


class ServiceBase:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    @property
    def name(self) -> str:
        return self.__class__.__name__
