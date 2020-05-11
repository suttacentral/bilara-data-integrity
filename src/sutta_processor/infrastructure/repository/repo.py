import pickle

from sutta_processor.application.domain_models.pali_canon.root import PaliCanonAggregate
from sutta_processor.application.domain_models.sutta_central.root import (
    SuttaCentralAggregate,
)
from sutta_processor.shared.config import Config


class FileRepository:
    PICKLE_EXTENSION = "pickle"

    def __init__(self, cfg: Config):
        self.cfg = cfg

    def get_all_sutta_central(self) -> SuttaCentralAggregate:
        root_aggregate = SuttaCentralAggregate.from_path(
            root_pth=self.cfg.root_pli_ms_path
        )
        return root_aggregate

    def get_all_pali_canon(self) -> PaliCanonAggregate:
        root_aggregate = PaliCanonAggregate.from_path(root_pth=self.cfg.pali_canon_path)
        return root_aggregate

    def dump_to_pickle(self, aggregate):
        out_pth = self.cfg.debug_dir / f"{aggregate.name()}.{self.PICKLE_EXTENSION}"
        out_pth.touch(exist_ok=True)
        with open(out_pth, "wb") as f:
            pickle.dump(obj=aggregate, file=f)

    def load_from_pickle(self, aggregate_cls):
        out_pth = self.cfg.debug_dir / f"{aggregate_cls.name()}.{self.PICKLE_EXTENSION}"
        out_pth.touch(exist_ok=True)
        with open(out_pth, "rb") as f:
            return pickle.load(file=f)
