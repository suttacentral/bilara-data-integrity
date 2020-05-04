from sutta_processor.application.domain_models.root import RootAggregate
from sutta_processor.shared.config import Config


class FileRepository:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def get_root(self) -> RootAggregate:
        root_aggregate = RootAggregate.from_path(root_pth=self.cfg.root_pli_ms_path)
        return root_aggregate
