import logging

from .bilara_check_comment import bilara_check_comment
from .bilara_check_html import bilara_check_html
from .bilara_check_root import bilara_check_root
from .bilara_check_translation import bilara_check_translation
from .bilara_cross_reference_uid_check import bilara_cross_reference_uid_check
from .bilara_load import bilara_load
from .ms_palicanon_load import ms_palicanon_load
from .ms_yuttadhammo_convert_to_html import ms_yuttadhammo_convert_to_html
from .ms_yuttadhammo_load import ms_yuttadhammo_load
from .reference_data_check import reference_data_check

log = logging.getLogger(__name__)


def noop(cfg):
    log.info("Script is working!")


__all__ = [
    "bilara_check_comment",
    "bilara_check_html",
    "bilara_check_root",
    "bilara_check_translation",
    "bilara_cross_reference_uid_check",
    "bilara_load",
    "ms_palicanon_load",
    "ms_yuttadhammo_convert_to_html",
    "ms_yuttadhammo_load",
    "noop",
    "reference_data_check",
]
