import json
import logging

from sutta_processor.application.domain_models import (
    BilaraRootAggregate,
    PaliCanonAggregate,
)
from sutta_processor.application.value_objects import UID, MsId
from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


class Engine:
    def __init__(self, concordance_path):
        with open(concordance_path) as f:
            self.mapping = json.load(f)
        self.other_id_set = {
            other_id for id_list in self.mapping for other_id in id_list
        }

    def is_uid_in_keys(self, uid: UID):
        return uid in self.mapping

    def is_pali_id_in_values(self, pali_id: MsId):
        return pali_id in self.other_id_set


class PaliConcordanceService:
    _engine: Engine = None

    def __init__(self, cfg: Config):
        self.cfg = cfg

    def check_our_and_pali_id(
        self, bilara_root: BilaraRootAggregate, pali_aggregate: PaliCanonAggregate
    ):
        check_callback = self.engine.is_uid_in_keys
        for sutta_uid in bilara_root.index:
            is_valid = check_callback(uid=sutta_uid)
            if is_valid:
                log.debug("Found sutta UID '%s' in corcondance", sutta_uid)
            else:
                log.warning(
                    "Sutta UID '%s' was NOT found in corcondance file!", sutta_uid
                )
        check_callback = self.engine.is_pali_id_in_values
        for pali_id in pali_aggregate.index:
            is_valid = check_callback(pali_id=pali_id)
            if is_valid:
                log.debug("Found pali_id '%s' in corcondance", pali_id)
            else:
                log.warning("pali_id '%s' was NOT found in corcondance file!", pali_id)

    @property
    def engine(self) -> Engine:
        if not self._engine:
            self._engine = Engine(concordance_path=self.cfg.pali_concordance_filepath)
        return self._engine
