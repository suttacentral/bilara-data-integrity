import logging
from pathlib import Path
from typing import List

from sutta_processor.application.check_service import CheckService
from sutta_processor.application.domain_models import (
    BilaraRootAggregate,
    BilaraVariantAggregate,
)
from sutta_processor.infrastructure.repository.repo import FileRepository
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


# noinspection PyDataclass
def bilara_check_variant(cfg: Config):
    cfg.repo: FileRepository
    cfg.check: CheckService
    bilara_root: BilaraRootAggregate = cfg.repo.bilara.get_root()
    bilara_variant: BilaraVariantAggregate = cfg.repo.bilara.get_variant()
    cfg.check.variant.get_wrong_uid_with_arrow(
        aggregate=bilara_variant, base_aggregate=bilara_root
    )
    cfg.check.variant.get_unknown_variants(aggregate=bilara_variant)
    cfg.check.get_unordered_segments(aggregate=bilara_variant)


# noinspection PyDataclass
def bilara_check_variant_from_files(cfg: Config, root_file_paths: List[Path], var_file_paths: List[Path]):
    cfg.repo: FileRepository
    cfg.check: CheckService
    bilara_root: BilaraRootAggregate = cfg.repo.bilara.get_root_from_files(file_paths=root_file_paths)
    bilara_variant: BilaraVariantAggregate = cfg.repo.bilara.get_variant_from_files(file_paths=var_file_paths)
    cfg.check.variant.get_wrong_uid_with_arrow(
        aggregate=bilara_variant, base_aggregate=bilara_root
    )
    cfg.check.variant.get_unknown_variants(aggregate=bilara_variant)
    cfg.check.get_unordered_segments(aggregate=bilara_variant)