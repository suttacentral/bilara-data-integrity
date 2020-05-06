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
    raw_source: str

    html_extractor = PaliHtmlExtractor

    @classmethod
    def from_file(cls, f_pth: Path) -> "PaliFileAggregate":
        raw_source = cls.get_raw_source(f_pth=f_pth)
        page = cls.get_page(raw_source=raw_source)
        crumb: PaliCrumb = cls.html_extractor.get_crumb(page=page)
        index: Dict[PaliMsId, PaliVersus] = cls.get_index(page=page)
        kwargs = {
            "crumb": crumb,
            "f_pth": f_pth,
            "index": index,
            "raw_source": raw_source,
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
    def get_raw_source(cls, f_pth: Path) -> str:
        with open(f_pth) as f:
            return f.read()

    @classmethod
    def get_page(cls, raw_source: str) -> _ElementTree:
        txt = raw_source.replace("<br>", "<br/>")
        return etree.fromstring(txt)
