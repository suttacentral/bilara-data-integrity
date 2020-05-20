import logging

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
