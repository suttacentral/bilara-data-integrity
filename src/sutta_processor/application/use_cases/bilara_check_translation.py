import logging

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
