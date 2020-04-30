import json

from sutta_processor.application.domain_models.sutta.mn import MnAggregate
from sutta_processor.shared.config import Config


class FileRepository:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def get_example(self, f_pth="sutta/mn/mn100_root-pli-ms.json") -> MnAggregate:
        with open(self.cfg.root_pli_ms_path / f_pth) as f:
            data = json.load(f)
        sutta = MnAggregate.from_dict(in_dto=data)
        return sutta
