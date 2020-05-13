import logging

from sutta_processor.application.domain_models import (
    BilaraCommentAggregate,
    BilaraHtmlAggregate,
    BilaraTranslationAggregate,
    BilaraVariantAggregate,
)
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


def bilara_cross_reference_uid_check(cfg: Config):
    bilara_root: BilaraHtmlAggregate = cfg.repo.bilara.get_root()
    bilara_html: BilaraHtmlAggregate = cfg.repo.bilara.get_html()
    bilara_comment: BilaraCommentAggregate = cfg.repo.bilara.get_comment()
    bilara_variant: BilaraVariantAggregate = cfg.repo.bilara.get_variant()
    bilara_translation: BilaraTranslationAggregate = cfg.repo.bilara.get_translation()
