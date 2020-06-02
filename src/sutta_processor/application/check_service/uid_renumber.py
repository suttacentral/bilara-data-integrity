import logging
from typing import Optional

from sutta_processor.application.check_service.base import ServiceBase
from sutta_processor.application.domain_models import (
    BilaraHtmlAggregate,
    BilaraReferenceAggregate,
    BilaraRootAggregate,
    ConcordanceAggregate,
    YuttaAggregate,
)
from sutta_processor.application.domain_models.bilara_html.root import HtmlVersus
from sutta_processor.application.domain_models.bilara_root.root import FileAggregate
from sutta_processor.application.value_objects import UID

log = logging.getLogger(__name__)


class UidRenumber(ServiceBase):
    bilara: BilaraRootAggregate
    html: BilaraHtmlAggregate

    def fix_missing_tassudanam(self):
        for file_aggregate in self.bilara.file_aggregates:
            self.process_file_aggregate(file_aggregate=file_aggregate)

    def process_file_aggregate(self, file_aggregate: FileAggregate):
        def update_root_file_index():
            new_index = {}
            for uid, versus in file_aggregate.index.items():
                if uid.key.key.startswith("foo"):
                    log.error("Replacing foo with uid: %s", foo_uid_to_replace)
                    new_uid = foo_uid_to_replace
                else:
                    new_uid = uid
                new_index[new_uid] = versus
            file_aggregate._replace_index(index=new_index)

        foo_found = False
        foo_uid_to_replace = None
        for uid in file_aggregate.index:
            if foo_found:
                # Verset form html data that is just before the foo
                prev_html_verse: HtmlVersus = self.get_prev_html_line(uid_after_foo=uid)
                if "uddana-intro" in prev_html_verse.verse:
                    foo_uid_to_replace = prev_html_verse.uid
                    # We can auto fix foo by assigning uid from prev verse of html file
                    break
                # TODO: handle it
                return

            elif uid.key.key.startswith("foo"):
                foo_found = True
        else:
            # No foo was found in this file
            return

        # We know that previous line in html file is 'uddana-intro' so the only missing
        #  piece is to update root file aggregate (and html) with correct uid
        update_root_file_index()

    def get_prev_html_line(self, uid_after_foo: UID) -> Optional[HtmlVersus]:

        prev_verse: HtmlVersus = ""  # ...
        for uid, versus in self.html.index.items():  # type: UID, HtmlVersus
            if uid == uid_after_foo:
                return prev_verse
            else:
                prev_verse = versus

    def add_aggregates(self, bilara: BilaraRootAggregate, html: BilaraHtmlAggregate):
        self.bilara = bilara
        self.html = html
