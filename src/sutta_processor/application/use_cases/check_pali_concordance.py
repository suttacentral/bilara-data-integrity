import logging

from sutta_processor.application.domain_models import SuttaCentralAggregate
from sutta_processor.application.domain_models.pali_canon.root import PaliCanonAggregate
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


def check_pali_concordance(cfg: Config):
    # TODO: remove lading from pickle
    log.info("Loading sutta from pickle")
    sutta_aggregate = cfg.repo.load_from_pickle(aggregate_cls=SuttaCentralAggregate)
    log.info("Loading pali canon from pickle")
    pali_aggregate = cfg.repo.load_from_pickle(aggregate_cls=PaliCanonAggregate)

    cfg.pali_concordance.check_our_and_pali_id(
        sutta_aggregate=sutta_aggregate, pali_aggregate=pali_aggregate
    )
