from sutta_processor.application.domain_models.sutta.mn import (
    MnAggregate,
    MnFileAggregate,
)
from sutta_processor.shared.config import Config


class FileRepository:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def get_example(self, f_pth="sutta/mn/mn100_root-pli-ms.json") -> MnFileAggregate:
        # with open(self.cfg.root_pli_ms_path / f_pth) as f:
        #     data = json.load(f)
        # sutta = MnFileAggregate.from_dict(in_dto=data)
        MnAggregate.from_path(root_pth=self.cfg.root_pli_ms_path)
        sutta = []
        return sutta
