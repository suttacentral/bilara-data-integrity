import logging

from sutta_processor.application.check_service import CheckService
from sutta_processor.infrastructure.repository.repo import FileRepository
from sutta_processor.shared.config import Config

from .bilara_check_comment import bilara_check_comment
from .bilara_check_html import bilara_check_html
from .bilara_check_references import bilara_check_references
from .bilara_check_root import bilara_check_root
from .bilara_check_translation import bilara_check_translation
from .bilara_check_variant import bilara_check_variant
from .bilara_check_duplicated_indexes import bilara_check_duplicated_indexes

log = logging.getLogger(__name__)


# noinspection PyDataclass
def run_all_checks(cfg: Config):
    cfg.repo: FileRepository
    cfg.check: CheckService
    #bilara_check_comment(cfg=cfg)
    bilara_check_html(cfg=cfg)
    #bilara_check_references(cfg=cfg)
    #bilara_check_root(cfg=cfg)
    #bilara_check_translation(cfg=cfg)
    #bilara_check_variant(cfg=cfg)
    #bilara_check_duplicated_indexes(cfg=cfg)
