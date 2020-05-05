import logging
from pathlib import Path
from typing import Dict, List, Tuple

import attr
from lxml import etree
from lxml.etree import _Element, _ElementTree

from sutta_processor.application.value_objects.uid import (
    PaliCrumb,
    PaliMsDivId,
    PaliMsId,
)
from sutta_processor.application.value_objects.verse import PaliVerse

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class PaliVersus:
    ms_id: PaliMsId
    msdiv_id: PaliMsDivId
    verse: PaliVerse


class PaliHtmlExtractor:
    @classmethod
    def get_crumb(cls, page: _ElementTree) -> PaliCrumb:
        last_href: _Element = page.xpath("//CRUMBS/a")[-1]
        pali_type = PaliCrumb(last_href.get("href"))
        return pali_type

    @classmethod
    def get_paragraphs(cls, page: _ElementTree) -> List[_Element]:
        return page.xpath("//body/p")

    @classmethod
    def get_ms_msdiv(cls, paragraph: _Element) -> Tuple[PaliMsId, PaliMsDivId]:
        a_ms = paragraph.xpath("./a[@class='ms']")[0]
        ms_id = PaliMsId(a_ms.get("id", ""))
        msdiv_id = PaliMsDivId("")
        try:
            a_msdiv = paragraph.xpath("./a[@class='msdiv']")[0]
            msdiv_id = PaliMsDivId(a_msdiv.get("id", ""))
        except IndexError:
            log.debug("No msdiv if for ms: '%s'", ms_id)
        return ms_id, msdiv_id

    @classmethod
    def get_verse(cls, paragraph: _Element) -> PaliVerse:
        text = paragraph.xpath("./text()")[0]
        versus = PaliVerse(text)
        return versus


@attr.s(frozen=True, auto_attribs=True)
class PaliFileAggregate:
    versets: Tuple[PaliVersus]
    index: Dict[PaliMsId, PaliVersus]

    crumb: PaliCrumb

    f_pth: Path
    page: _ElementTree

    html_extractor = PaliHtmlExtractor

    @classmethod
    def from_file(cls, f_pth: Path) -> "PaliFileAggregate":
        page = cls.get_page(f_pth=f_pth)
        crumb: PaliCrumb = cls.html_extractor.get_crumb(page=page)
        index: Dict[PaliMsId, PaliVersus] = cls.get_index(page=page)
        kwargs = {
            "crumb": crumb,
            "f_pth": f_pth,
            "index": index,
            "page": page,
            "versets": tuple(index.values()),
        }
        return cls(**kwargs)

    @classmethod
    def get_index(cls, page: _ElementTree) -> Dict[PaliMsId, PaliVersus]:
        page_paragraphs = cls.html_extractor.get_paragraphs(page=page)
        dict_args = (cls.get_versus(paragraph=p) for p in page_paragraphs)
        index = {ms_id: versus for ms_id, versus in dict_args}
        return index

    @classmethod
    def get_versus(cls, paragraph: _Element) -> Tuple[PaliMsId, PaliVersus]:
        ms_id, msdiv_id = cls.html_extractor.get_ms_msdiv(paragraph=paragraph)
        verse = cls.html_extractor.get_verse(paragraph=paragraph)
        versus = PaliVersus(ms_id=ms_id, msdiv_id=msdiv_id, verse=verse)
        return ms_id, versus

    @classmethod
    def get_page(cls, f_pth: Path) -> _ElementTree:
        with open(f_pth) as f:
            return etree.parse(f)
