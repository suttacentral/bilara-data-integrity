import logging

from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


def ms_yuttadhammo_convert_to_html(cfg: Config):
    root_aggregate = cfg.repo.yutta.get_xml_data_for_conversion()
    log.info("Got root aggregate: %s", root_aggregate)
    cfg.repo.yutta.save_yutta_html_files(aggregate=root_aggregate)
    log.info("Saved htmls files: %s", root_aggregate)
