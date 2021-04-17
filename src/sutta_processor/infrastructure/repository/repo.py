import json
import logging
import os
import pickle
import stat
from pathlib import Path
from typing import List, Set

from sutta_processor.application.domain_models import (
    BilaraCommentAggregate,
    BilaraHtmlAggregate,
    BilaraReferenceAggregate,
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
from sutta_processor.application.domain_models.bilara_concordance.root import (
    ConcordanceAggregate,
    ConcordanceFileAggregate,
)
from sutta_processor.application.domain_models.bilara_translation.root import (
    BilaraTranslationFileAggregate,
)
from sutta_processor.shared.config import NULL_PTH, Config

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
    _root: BilaraRootAggregate = None
    _html: BilaraHtmlAggregate = None
    _comment: BilaraCommentAggregate = None
    _variant: BilaraVariantAggregate = None
    _translation: BilaraTranslationAggregate = None
    _reference: BilaraReferenceAggregate = None

    def __init__(self, cfg: Config):
        self.cfg = cfg

    def get_root(self) -> BilaraRootAggregate:
        if not self._root:
            self._root = BilaraRootAggregate.from_path(
                exclude_dirs=self.cfg.exclude_dirs,
                root_pth=self.cfg.bilara_root_path,
                root_langs=self.cfg.bilara_root_langs,
            )
        return self._root

    def get_root_from_files(self, file_paths: List[Path]) -> BilaraRootAggregate:
        """A version of the get_root function that works on a list of files as a pathlib.Path obect."""
        if not self._root:
            self._root = BilaraRootAggregate.from_file_paths(
                exclude_dirs=self.cfg.exclude_dirs,
                file_paths=file_paths,
                root_langs=self.cfg.bilara_root_langs,
            )
        return self._root

    def get_html(self) -> BilaraHtmlAggregate:
        if not self._html:
            self._html = BilaraHtmlAggregate.from_path(
                exclude_dirs=self.cfg.exclude_dirs,
                root_pth=self.cfg.bilara_html_path
            )
        return self._html

    def get_html_from_files(self, file_paths: List[Path]) -> BilaraHtmlAggregate:
        """A version of the get_html function that works on a list of files as a pathlib.Path obect."""
        if not self._html:
            self._html = BilaraHtmlAggregate.from_file_paths(
                exclude_dirs=self.cfg.exclude_dirs,
                file_paths=file_paths
            )
        return self._html

    def get_comment(self) -> BilaraCommentAggregate:
        if not self._comment:
            self._comment = BilaraCommentAggregate.from_path(
                exclude_dirs=self.cfg.exclude_dirs,
                root_pth=self.cfg.bilara_comment_path
            )
        return self._comment

    def get_comment_from_files(self, file_paths: List[Path]) -> BilaraCommentAggregate:
        if not self._comment:
            self._comment = BilaraCommentAggregate.from_file_paths(
                exclude_dirs=self.cfg.exclude_dirs,
                file_paths=file_paths,
            )
        return self._comment

    def get_variant(self) -> BilaraVariantAggregate:
        if not self._variant:
            self._variant = BilaraVariantAggregate.from_path(
                exclude_dirs=self.cfg.exclude_dirs,
                root_pth=self.cfg.bilara_variant_path
            )
        return self._variant

    def get_variant_from_files(self, file_paths: List[Path]) -> BilaraVariantAggregate:
        if not self._variant:
            self._variant = BilaraVariantAggregate.from_file_paths(
                exclude_dirs=self.cfg.exclude_dirs,
                file_paths=file_paths,
            )
        return self._variant

    def get_translation(self) -> BilaraTranslationAggregate:
        if not self._translation:
            self._translation = BilaraTranslationAggregate.from_path(
                exclude_dirs=self.cfg.exclude_dirs,
                root_pth=self.cfg.bilara_translation_path,
            )
        return self._translation

    def get_translation_from_files(self, file_paths: List[Path]) -> BilaraTranslationAggregate:
        if not self._translation:
            self._translation = BilaraTranslationAggregate.from_file_paths(
                exclude_dirs=self.cfg.exclude_dirs,
                file_paths=file_paths,
            )
        return self._translation

    def get_reference(self) -> BilaraReferenceAggregate:
        if not self._reference:
            self._reference = BilaraReferenceAggregate.from_path(
                exclude_dirs=self.cfg.exclude_dirs,
                root_pth=self.cfg.reference_root_path
            )
        return self._reference

    def get_reference_from_files(self, file_paths: List[Path]) -> BilaraReferenceAggregate:
        if not self._reference:
            self._reference = BilaraReferenceAggregate.from_file_paths(
                exclude_dirs=self.cfg.exclude_dirs,
                file_paths=file_paths,
            )
        return self._reference

    def get_concordance(self) -> ConcordanceAggregate:
        aggregate = ConcordanceAggregate.from_path(
            root_pth=self.cfg.pali_concordance_filepath
        )
        return aggregate

    def save(self, aggregate: BaseRootAggregate):
        log.info("Saving '%s'", aggregate.name())
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

    def generate_diff_feedback_file(self, diff: Set[str], name: str = ""):
        if self.cfg.debug_dir == NULL_PTH:
            log.error("To generate diff file, add valid 'debug_dir' to your settings.")
            return
        if not diff:
            return

        f_name = f"grep_for_feedback_{name}.sh" if name else f"grep_for_feedback.sh"
        exclude_dir_name = "feedback"
        out_lines = [
            "#!/bin/sh",
            f"mkdir -pv {exclude_dir_name}",
            "",
        ]
        echo_templ = f"echo Searching %s/{len(diff)}. UID: '%s'"
        grep_templ = (
            f"ack --break --heading -C 2 " f"'%s' --json > ./{exclude_dir_name}/%s.txt"
        )
        for i, uid in enumerate(sorted(diff), start=1):
            out_lines.append(echo_templ % (i, uid))
            out_lines.append(grep_templ % (uid, uid))
        out_lines.append("")

        # noinspection PyTypeChecker
        with open(self.cfg.debug_dir / f_name, "w") as fd:
            fd.write("\n".join(out_lines))
            mode = os.fstat(fd.fileno()).st_mode
            mode |= stat.S_IXUSR
            os.fchmod(fd.fileno(), stat.S_IMODE(mode))
        log.info("Saved feedback file in '%s'", self.cfg.debug_dir / f_name)
