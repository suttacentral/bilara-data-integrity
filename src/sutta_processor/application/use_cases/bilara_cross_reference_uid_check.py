import logging

from sutta_processor.application.domain_models.bilara_html.root import (
    BilaraHtmlAggregate,
)
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


def bilara_cross_reference_uid_check(cfg: Config):
    root_aggregate: BilaraHtmlAggregate = cfg.repo.bilara.get_html()
