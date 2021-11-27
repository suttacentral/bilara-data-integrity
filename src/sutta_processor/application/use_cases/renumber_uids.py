import logging

from sutta_processor.application.check_service import CheckService
from sutta_processor.application.domain_models import (
    BilaraHtmlAggregate,
    BilaraReferenceAggregate,
    BilaraRootAggregate,
)
from sutta_processor.infrastructure.repository.repo import FileRepository
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


# noinspection PyDataclass
def renumber_uids(cfg: Config):
    cfg.repo: FileRepository
    cfg.check: CheckService

    bilara: BilaraRootAggregate = cfg.repo.bilara.get_root()
    html: BilaraHtmlAggregate = cfg.repo.bilara.get_html()
    cfg.check.renumber.add_aggregates(bilara=bilara, html=html)
    cfg.check.renumber.fix_missing_tassudanam()
    cfg.repo.bilara.save(aggregate=bilara)
    cfg.repo.bilara.save(aggregate=html)
