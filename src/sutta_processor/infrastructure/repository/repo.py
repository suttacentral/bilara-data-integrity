import json
import logging
import pickle

from sutta_processor.application.domain_models import (
    BilaraCommentAggregate,
    BilaraHtmlAggregate,
    BilaraRootAggregate,
    BilaraTranslationAggregate,
    BilaraVariantAggregate,
    PaliCanonAggregate,
    YuttaAggregate,
)
from sutta_processor.application.domain_models.base import (
    BaseFileAggregate,
    BaseRootAggregate,
)
from sutta_processor.application.domain_models.bilara_translation.root import (
    BilaraTranslationFileAggregate,
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


class BilaraRepo:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def get_root(self) -> BilaraRootAggregate:
        root_aggregate = BilaraRootAggregate.from_path(
            root_pth=self.cfg.bilara_root_path
        )
        return root_aggregate

    def get_html(self) -> BilaraHtmlAggregate:
        aggregate = BilaraHtmlAggregate.from_path(root_pth=self.cfg.bilara_html_path)
        return aggregate

    def get_comment(self) -> BilaraCommentAggregate:
        aggregate = BilaraCommentAggregate.from_path(
            root_pth=self.cfg.bilara_comment_path
        )
        return aggregate

    def get_variant(self) -> BilaraVariantAggregate:
        aggregate = BilaraVariantAggregate.from_path(
            root_pth=self.cfg.bilara_variant_path
        )
        return aggregate

    def get_translation(self) -> BilaraTranslationAggregate:
        aggregate = BilaraTranslationAggregate.from_path(
            root_pth=self.cfg.bilara_translation_path
        )
        return aggregate

    def save(self, aggregate: BaseRootAggregate):
        for each_file in aggregate.file_aggregates:  # type: BaseFileAggregate
            with open(each_file.f_pth, "w") as f:
                json.dump(each_file.data, f, indent=2, ensure_ascii=False)


class FileRepository:
    PICKLE_EXTENSION = "pickle"

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.yutta: YuttadhammoRepo = YuttadhammoRepo(cfg=cfg)
        self.bilara: BilaraRepo = BilaraRepo(cfg=cfg)

    def get_all_pali_canon(self) -> PaliCanonAggregate:
        root_aggregate = PaliCanonAggregate.from_path(root_pth=self.cfg.pali_canon_path)
        return root_aggregate

    def dump_pickle(self, aggregate):
        out_pth = self.cfg.debug_dir / f"{aggregate.name()}.{self.PICKLE_EXTENSION}"
        out_pth.touch(exist_ok=True)
        with open(out_pth, "wb") as f:
            pickle.dump(obj=aggregate, file=f)

    def load_pickle(self, aggregate_cls):
        out_pth = self.cfg.debug_dir / f"{aggregate_cls.name()}.{self.PICKLE_EXTENSION}"
        out_pth.touch(exist_ok=True)
        with open(out_pth, "rb") as f:
            return pickle.load(file=f)
