import logging
from pathlib import Path
from typing import List

from sutta_processor.application.check_service import CheckService
from sutta_processor.application.domain_models import (
    BilaraCommentAggregate,
    BilaraRootAggregate,
)
from sutta_processor.infrastructure.repository.repo import FileRepository
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


# noinspection PyDataclass
def bilara_check_comment(cfg: Config):
    cfg.repo: FileRepository
    cfg.check: CheckService
    bilara_root: BilaraRootAggregate = cfg.repo.bilara.get_root()
    bilara_comm: BilaraCommentAggregate = cfg.repo.bilara.get_comment()
    cfg.check.get_comment_surplus_segments(
        check_aggregate=bilara_comm, base_aggregate=bilara_root
    )
    cfg.check.get_unordered_segments(aggregate=bilara_comm)

# noinspection PyDataclass
def bilara_check_comment_from_files(cfg: Config, comment_file_paths: List[Path], root_file_paths: List[Path]):
    cfg.repo: FileRepository
    cfg.check: CheckService
    bilara_root: BilaraRootAggregate = cfg.repo.bilara.get_root_from_files(file_paths=root_file_paths)
    bilara_comm: BilaraCommentAggregate = cfg.repo.bilara.get_comment_from_files(file_paths=comment_file_paths)
    cfg.check.get_comment_surplus_segments(
        check_aggregate=bilara_comm, base_aggregate=bilara_root
    )
    cfg.check.get_unordered_segments(aggregate=bilara_comm)
