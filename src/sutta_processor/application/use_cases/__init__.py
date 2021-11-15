import logging

from .bilara_check_comment import bilara_check_comment
from .bilara_check_html import bilara_check_html
from .bilara_check_references import bilara_check_references
from .bilara_check_root import bilara_check_root
from .bilara_check_translation import bilara_check_translation
from .bilara_check_variant import bilara_check_variant
from .bilara_load import bilara_load
from .fix_headers_uid import fix_headers_uid
from .renumber_uids import renumber_uids
from .run_all_checks import run_all_checks
from .check_all_changes import check_all_changes
from .check_migration import check_migration

log = logging.getLogger(__name__)


def noop(cfg):
    log.info("Script is working!")


__all__ = [
    "bilara_check_comment",
    "bilara_check_html",
    "bilara_check_references",
    "bilara_check_root",
    "bilara_check_translation",
    "bilara_check_variant",
    "bilara_load",
    "bilara_check_duplicated_indexes",
    "check_all_changes",
    "fix_headers_uid",
    "noop",
    "renumber_uids",
    "run_all_checks",
    "check_migration",
]
