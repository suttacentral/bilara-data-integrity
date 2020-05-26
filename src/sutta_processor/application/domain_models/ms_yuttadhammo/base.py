import logging
from pathlib import Path
from typing import Dict, Tuple

import attr
from lxml.etree import _Element

from sutta_processor.application.value_objects import MsId, MsVerse

from ..base import BaseFileAggregate, BaseVersus
from .extractors import YuttaExtractor

log = logging.getLogger(__name__)


@attr.s(frozen=True, auto_attribs=True)
class YuttaVersus(BaseVersus):
    ms_id: MsId
    verse: MsVerse = attr.ib(converter=MsVerse)
    raw_uid: None = attr.ib(init=False, default=None)

    def __attrs_post_init__(self):
        pass


@attr.s(frozen=True, auto_attribs=True)
class YuttaFileAggregate(BaseFileAggregate):
    versets: Tuple[YuttaVersus]
    index: Dict[MsId, YuttaVersus]

    raw_xml: str
    raw_html: str

    _html_cleaned: str = ""

    extractor = YuttaExtractor

    @classmethod
    def from_file(cls, f_pth: Path) -> "YuttaFileAggregate":
        """
        :param f_pth: Must be path to cleaned html file
        """
        raw_html = cls.get_raw_source(f_pth=f_pth)
        page = cls.extractor.get_page_from_html(html=raw_html)
        index: Dict[MsId, YuttaVersus] = cls.get_index(page=page)

        kwargs = {
            "f_pth": f_pth,
            "index": index,
            "raw_html": raw_html,
            "raw_xml": "",
            "versets": tuple(index.values()),
            "errors": tuple(),
        }
        return cls(**kwargs)

    @classmethod
    def from_dict(cls, in_dto: dict, f_pth: Path) -> "YuttaFileAggregate":
        return cls(**in_dto)

    @classmethod
    def get_index(cls, page: _Element) -> Dict[MsId, YuttaVersus]:
        id_nodes = cls.extractor.get_id_nodes(page=page)
        dict_args = (cls.get_versus(node=n) for n in id_nodes)
        index = {ms_id: versus for ms_id, versus in dict_args}
        return index

    @classmethod
    def get_versus(cls, node: _Element) -> Tuple[MsId, YuttaVersus]:
        ms_id = MsId.from_xml_id(cls.extractor.get_ms_id(node=node))
        verse = MsVerse(cls.extractor.get_verse(node=node))
        versus = YuttaVersus(ms_id=ms_id, verse=verse)
        return ms_id, versus

    @property
    def html_cleaned(self) -> str:
        if not self._html_cleaned:
            cleaned_str = (
                self.raw_html.replace("class=b", 'class="b"')
                .replace("class=h", 'class="h"')
                .replace("class=plcb", 'class="plcb"')
                .replace("&nbsp;", " ")
            )
            cleaned_str = f"<html>{cleaned_str}</html>"
            cleaned_str = self.extractor.clean_html(cleaned_html=cleaned_str)
            object.__setattr__(self, "_html_cleaned", cleaned_str)

        return self._html_cleaned

    @classmethod
    def get_raw_source(cls, f_pth: Path) -> str:
        with open(f_pth) as f:
            return f.read()

    @classmethod
    def convert_to_html(cls, f_pth: Path) -> "YuttaFileAggregate":
        """ When doing the conversion there won't be any indexes loaded. """
        index = {}
        raw_xml = cls.get_raw_source(f_pth=f_pth)
        raw_html = cls.extractor.get_html_from_xml(xml_string=raw_xml)
        kwargs = {
            "f_pth": f_pth,
            "index": index,
            "raw_xml": raw_xml,
            "raw_html": raw_html,
            "versets": tuple(index.values()),
            "errors": tuple(),
        }
        return cls.from_dict(in_dto=kwargs, f_pth=f_pth)
