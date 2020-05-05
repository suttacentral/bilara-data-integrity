import logging
from pathlib import Path
from typing import List, Tuple

import attr
from lxml import etree
from lxml.etree import _Element, _ElementTree

from sutta_processor.application.value_objects.uid import (
    PaliCrumb,
    PaliMsDivId,
    PaliMsId,
)

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class PaliVersus:
    ms_id: PaliMsId
    msdiv_id: PaliMsDivId


class PaliHtmlExtractor:
    @classmethod
    def get_pali_crumb(cls, page: _ElementTree) -> PaliCrumb:
        last_href: _Element = page.xpath("//CRUMBS/a")[-1]
        pali_type = PaliCrumb(last_href.get("href"))
        return pali_type

    @classmethod
    def get_pali_paragraphs(cls, page: _ElementTree) -> List[_Element]:
        return page.xpath("//body/p")

    @classmethod
    def get_pali_ms_msdiv(cls, paragraph: _Element) -> Tuple[PaliMsId, PaliMsDivId]:
        a_ms = paragraph.xpath("./a[@class='ms']")[0]
        ms_id = PaliMsId(a_ms.get("id", ""))
        msdiv_id = PaliMsDivId("")
        try:
            a_msdiv = paragraph.xpath("./a[@class='msdiv']")[0]
            msdiv_id = PaliMsDivId(a_msdiv.get("id", ""))
        except IndexError:
            log.debug("No msdiv if for ms: '%s'", ms_id)
        return ms_id, msdiv_id


@attr.s(frozen=True, auto_attribs=True)
class PaliFileAggregate:
    # parts: Tuple[PaliVersus]
    # index: Dict[UID, PaliVersus]

    f_pth: Path
    page: _ElementTree

    html_extractor = PaliHtmlExtractor

    @classmethod
    def from_file(cls, f_pth: Path) -> "PaliFileAggregate":
        page = cls.get_page(f_pth=f_pth)
        pali_crumb = cls.html_extractor.get_pali_crumb(page=page)
        pali_paragraph = cls.html_extractor.get_pali_paragraphs(page=page)
        versets = []
        for p in pali_paragraph:
            versets.append(cls.get_verse(paragraph=p))
        print("versets", versets)
        return cls(f_pth=f_pth, page=page)

    @classmethod
    def get_verse(cls, paragraph: _Element) -> PaliVersus:
        ms_id, msdiv_id = cls.html_extractor.get_pali_ms_msdiv(paragraph=paragraph)
        versus = PaliVersus(ms_id=ms_id, msdiv_id=msdiv_id)
        return versus

    @classmethod
    def get_page(cls, f_pth: Path) -> _ElementTree:
        with open(f_pth) as f:
            return etree.parse(f)
