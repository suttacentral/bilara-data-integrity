import logging
import pickle

from sutta_processor.application.domain_models import (
    PaliCanonAggregate,
    SuttaCentralAggregate,
    YuttaAggregate,
)
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


class YuttadhammoRepo:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def get_aggregate(self) -> YuttaAggregate:
        root_aggregate = YuttaAggregate.from_path(root_pth=self.cfg.ms_yuttadhammo_path)
        return root_aggregate

    def get_xml_data_for_conversion(self) -> YuttaAggregate:
        root_aggregate = YuttaAggregate.convert_to_html(
            root_pth=self.cfg.ms_yuttadhammo_path
        )
        return root_aggregate

    @classmethod
    def save_yutta_html_files(cls, aggregate: YuttaAggregate):
        def save_file(f_aggregate):
            f_pth = str(f_aggregate.f_pth).replace("xml", "html")
            with open(f_pth, "w") as f:
                f.write(f_aggregate.html_cleaned)

        for file_aggregate in aggregate.file_aggregates:
            log.trace("Saving html file for xml: '%s'", file_aggregate.f_pth.name)
            save_file(f_aggregate=file_aggregate)


class FileRepository:
    PICKLE_EXTENSION = "pickle"

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.yutta: YuttadhammoRepo = YuttadhammoRepo(cfg=cfg)

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
