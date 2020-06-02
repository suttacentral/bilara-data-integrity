from sutta_processor.application.check_service.base import ServiceBase
from sutta_processor.application.domain_models import (
    BilaraHtmlAggregate,
    BilaraReferenceAggregate,
    BilaraRootAggregate,
    ConcordanceAggregate,
    YuttaAggregate,
)
from sutta_processor.application.domain_models.bilara_root.root import FileAggregate


class UidRenumber(ServiceBase):
    # def __init__(
    #     self, cfg: Config, bilara: BilaraRootAggregate, html: BilaraHtmlAggregate,
    # ):
    #     super().__init__(cfg)
    #     self.bilara = bilara
    #     self.html = html

    def fix_missing_tassudanam(self, bilara: BilaraRootAggregate):
        for file_aggregate in bilara.file_aggregates:
            self.process_file_aggregate(file_aggregate=file_aggregate)

    def process_file_aggregate(self, file_aggregate: FileAggregate):
        for uid in file_aggregate.index:
            if uid.key.key.startswith("foo"):
                print("Found foo in:", file_aggregate)
