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
from sutta_processor.application.domain_models.bilara_html.root import (
    BilaraHtmlFileAggregate,
    HtmlVersus,
)
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

        def update_html_file_index(next_uid):
            html_f_aggregate: BilaraHtmlFileAggregate = self.html.file_index[next_uid]
            new_index = {}
            prev_uid = None
            for uid, versus in html_f_aggregate.index.items():
                if uid == next_uid:
                    verse = HtmlVersus(
                        raw_uid=foo_uid_to_replace,
                        verse="<p class='uddana-intro'>{}</p>",
                    )
                    prev_verse = new_index.pop(prev_uid)
                    new_index[foo_uid_to_replace] = verse
                    new_index[prev_uid] = prev_verse

                new_index[uid] = versus
                prev_uid = uid
            html_f_aggregate._replace_index(index=new_index)

        foo_found = False
        foo_uid_to_replace = None
        handle_foo_not_in_html = False
        for uid in file_aggregate.index:
            if handle_foo_not_in_html:
                foo_uid_to_replace = uid.get_header_uid()
                if not foo_uid_to_replace:
                    # Uid is in the middle of sequence so need to be manualy renumbered
                    return
                update_html_file_index(next_uid=uid)
                update_root_file_index()
                return

            elif foo_found:
                # Verset form html data that is just before the foo
                prev_html_verse: HtmlVersus = self.get_prev_html_line(uid_after_foo=uid)
                if "uddana-intro" in prev_html_verse.verse:
                    foo_uid_to_replace = prev_html_verse.uid
                    # We can auto fix foo by assigning uid from prev verse of html file
                    # We know that previous line in html file is 'uddana-intro' so
                    #  the only missing piece is to update root file aggregate (and
                    #  html) with correct uid
                    update_root_file_index()
                    return
                # If foo not in html we need to get next segment so that we can
                #  zero it out to make it to a header
                handle_foo_not_in_html = True
                continue
            elif uid.key.key.startswith("foo"):
                foo_found = True
        else:
            # No foo was found in this file
            return

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
