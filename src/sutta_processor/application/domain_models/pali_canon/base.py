import logging
from pathlib import Path
from typing import Dict, Tuple

import attr
from lxml import etree
from lxml.etree import _Element, _ElementTree

from sutta_processor.application.value_objects.uid import (
    PaliCrumb,
    PaliMsDivId,
    PaliMsId,
)
from sutta_processor.application.value_objects.verse import PaliVerse

from .extractors import PaliHtmlExtractor

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class PaliVersus:
    ms_id: PaliMsId
    msdiv_id: PaliMsDivId
    verse: PaliVerse


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
