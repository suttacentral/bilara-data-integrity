import logging

from sutta_processor.application.check_service import CheckService
from sutta_processor.application.domain_models import (
    BilaraCommentAggregate,
    BilaraRootAggregate,
    BilaraTranslationAggregate,
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
    cfg.check.get_surplus_segments(
        check_aggregate=bilara_comm, base_aggregate=bilara_root
    )
