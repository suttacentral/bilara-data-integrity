import logging

from .check_reference_data import check_reference_data
from .load_all_data import load_all_data
from .loading_palicanon import loading_palicanon

log = logging.getLogger(__name__)


def noop(cfg):
    log.info("Script is working!")


__all__ = [
    "check_reference_data",
    "load_all_data",
    "loading_palicanon",
    "noop",
]
