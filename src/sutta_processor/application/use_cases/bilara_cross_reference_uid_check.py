import logging

from sutta_processor.application.domain_models import (
    BilaraCommentAggregate,
    BilaraHtmlAggregate,
    BilaraRootAggregate,
    BilaraTranslationAggregate,
    BilaraVariantAggregate,
)
from sutta_processor.infrastructure.repository.repo import FileRepository
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


def bilara_cross_reference_uid_check(cfg: Config):
    # noinspection PyDataclass
    cfg.repo: FileRepository
    bilara_root: BilaraRootAggregate = cfg.repo.bilara.get_root()
    bilara_html: BilaraHtmlAggregate = cfg.repo.bilara.get_html()
    bilara_comment: BilaraCommentAggregate = cfg.repo.bilara.get_comment()
    bilara_variant: BilaraVariantAggregate = cfg.repo.bilara.get_variant()
    bilara_translation: BilaraTranslationAggregate = cfg.repo.bilara.get_translation()
