import logging
from pathlib import Path
from typing import List

from sutta_processor.application.check_service import CheckService
from sutta_processor.application.domain_models import (
    BilaraHtmlAggregate,
    BilaraTranslationAggregate,
)
from sutta_processor.infrastructure.repository.repo import FileRepository
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


# noinspection PyDataclass
def bilara_check_translation(cfg: Config):
    cfg.repo: FileRepository
    cfg.check: CheckService
    bilara_html: BilaraHtmlAggregate = cfg.repo.bilara.get_html()
    bilara_tran: BilaraTranslationAggregate = cfg.repo.bilara.get_translation()
    cfg.check.get_surplus_segments(
        check_aggregate=bilara_tran, base_aggregate=bilara_html
    )
    cfg.check.get_unordered_segments(aggregate=bilara_tran)


# noinspection PyDataclass
def bilara_check_translation_from_files(cfg: Config, html_file_paths: List[Path], trans_file_paths: List[Path]):
    cfg.repo: FileRepository
    cfg.check: CheckService
    bilara_html: BilaraHtmlAggregate = cfg.repo.bilara.get_html_from_files(file_paths=html_file_paths)
    bilara_tran: BilaraTranslationAggregate = cfg.repo.bilara.get_root_from_files(file_paths=trans_file_paths)
    cfg.check.get_surplus_segments(
        check_aggregate=bilara_tran, base_aggregate=bilara_html
    )
    cfg.check.get_unordered_segments(aggregate=bilara_tran)
