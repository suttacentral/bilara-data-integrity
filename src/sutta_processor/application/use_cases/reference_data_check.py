import logging

from sutta_processor.application.check_service import CheckService
from sutta_processor.application.domain_models import (
    BilaraReferenceAggregate,
    BilaraRootAggregate,
    ConcordanceAggregate,
)
from sutta_processor.application.value_objects import UID
from sutta_processor.infrastructure.repository.repo import FileRepository
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


class DiffGenerator:
    def __init__(self, aggregate_t1, aggregate_t2):
        self.aggregate_t2: BilaraRootAggregate = aggregate_t2
        self.aggregate_t1: BilaraRootAggregate = aggregate_t1

    def save_diff_csv(self):
        [UID, UID]
        new_idx_seen = set()
        missing_ids = set()
        no_match_ids = {}
        for old_idx, old_verse in self.aggregate_t1.index.items():
            new_verse = self.aggregate_t2.index.pop(old_idx, None)
            if new_verse is None:
                missing_ids.add(old_idx)
            elif new_verse.verse.tokens == old_verse.verse.tokens:
                new_idx_seen.add(old_idx)
            else:
                no_match_ids[old_idx] = [old_verse, new_verse]

        print("-" * 40)
        print("new ids left:", len(self.aggregate_t2.index))
        print("new_idx_seen:", len(new_idx_seen))
        print("-" * 40)


# noinspection PyDataclass
def reference_data_check(cfg: Config):
    cfg.repo: FileRepository
    cfg.check: CheckService
    # yutta_aggregate: YuttaAggregate = cfg.repo.yutta.get_aggregate()
    reference: BilaraReferenceAggregate = cfg.repo.bilara.get_reference()
    concordance: ConcordanceAggregate = cfg.repo.bilara.get_concordance()
    cfg.check.reference.update_references_from_concordance(
        reference=reference, concordance=concordance
    )

    # cfg.check.save_csv_diff(bilara=bilara_root, bilara_begin=bilara_root_begin)
    # cfg.check.reference.get_missing_ms_id_from_reference(aggregate=yutta_aggregate)
    # cfg.check.reference.log_wrong_ms_id_in_reference_data(aggregate=yutta_aggregate)
    # cfg.check.reference.log_wrong_uid_in_reference_data(bilara=bilara_root)
