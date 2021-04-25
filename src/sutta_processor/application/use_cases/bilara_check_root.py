import logging
from pathlib import Path
from typing import List

from sutta_processor.application.check_service import CheckService
from sutta_processor.application.domain_models import BilaraRootAggregate
from sutta_processor.infrastructure.repository.repo import FileRepository
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


# noinspection PyDataclass
def bilara_check_root(cfg: Config):
    cfg.repo: FileRepository
    cfg.check: CheckService
    root_aggregate: BilaraRootAggregate = cfg.repo.bilara.get_root()
    cfg.check.check_uid_sequence_in_file(aggregate=root_aggregate)
    diff = cfg.check.get_duplicated_verses_next_to_each_other(aggregate=root_aggregate)
    diff = cfg.check.get_empty_verses(aggregate=root_aggregate)


# noinspection PyDataclass
def bilara_check_root_from_files(cfg: Config, root_file_paths: List[Path]):
    cfg.repo: FileRepository
    cfg.check: CheckService
    root_aggregate: BilaraRootAggregate = cfg.repo.bilara.get_root_from_files(file_paths=root_file_paths)
    cfg.check.check_uid_sequence_in_file(aggregate=root_aggregate)
    diff = cfg.check.get_duplicated_verses_next_to_each_other(aggregate=root_aggregate)
    diff = cfg.check.get_empty_verses(aggregate=root_aggregate)
