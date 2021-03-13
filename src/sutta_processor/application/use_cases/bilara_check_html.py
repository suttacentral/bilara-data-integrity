import logging
from pathlib import Path
from typing import List

from sutta_processor.application.check_service import CheckService
from sutta_processor.application.domain_models import (
    BilaraHtmlAggregate,
    BilaraRootAggregate,
)
from sutta_processor.infrastructure.repository.repo import FileRepository
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


# noinspection PyDataclass
def bilara_check_html(cfg: Config):
    cfg.repo: FileRepository
    cfg.check: CheckService
    bilara_html: BilaraHtmlAggregate = cfg.repo.bilara.get_html()
    cfg.check.html.is_0_in_header_uid(aggregate=bilara_html)
    bilara_root: BilaraRootAggregate = cfg.repo.bilara.get_root()
    diff = cfg.check.html.get_missing_segments(
        html_aggregate=bilara_html, base_aggregate=bilara_root
    )
    cfg.check.get_unordered_segments(aggregate=bilara_html)

# noinspection PyDataclass
def bilara_check_html_from_files(cfg: Config, html_file_paths: List[Path], root_file_paths: List[Path]):
    cfg.repo: FileRepository
    cfg.check: CheckService
    bilara_html: BilaraHtmlAggregate = cfg.repo.bilara.get_html_from_files(file_paths=html_file_paths)
    cfg.check.html.is_0_in_header_uid(aggregate=bilara_html)
    bilara_root: BilaraRootAggregate = cfg.repo.bilara.get_root_from_files(file_paths=root_file_paths)
    diff = cfg.check.html.get_missing_segments(
        html_aggregate=bilara_html, base_aggregate=bilara_root
    )
    cfg.check.get_unordered_segments(aggregate=bilara_html)
