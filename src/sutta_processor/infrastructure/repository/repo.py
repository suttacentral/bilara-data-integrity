from sutta_processor.application.domain_models.sutta_central.root import (
    SuttaCentralAggregate,
)
from sutta_processor.shared.config import Config


class FileRepository:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def get_root(self) -> SuttaCentralAggregate:
        root_aggregate = SuttaCentralAggregate.from_path(
            root_pth=self.cfg.root_pli_ms_path
        )
        return root_aggregate
