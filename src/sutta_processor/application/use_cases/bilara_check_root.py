import logging

from sutta_processor.application.check_service import CheckService
from sutta_processor.application.domain_models import BilaraRootAggregate
from sutta_processor.infrastructure.repository.repo import FileRepository
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


# noinspection PyDataclass
def bilara_check_root(cfg: Config):
    cfg.repo: FileRepository
    cfg.check: CheckService
    root_aggregate: BilaraRootAggregate = cfg.repo.bilara.get_root()
    cfg.check.check_uid_sequence_in_file(aggregate=root_aggregate)
    diff = cfg.check.get_duplicated_versus_next_to_each_other(aggregate=root_aggregate)
    cfg.repo.generate_diff_feedback_file(diff=diff)
    diff = cfg.check.get_empty_verses(aggregate=root_aggregate)
    cfg.repo.generate_diff_feedback_file(diff=diff, name="empty_versus")
    cfg.check.reference.get_wrong_segments_based_on_nya(bilara=root_aggregate)
