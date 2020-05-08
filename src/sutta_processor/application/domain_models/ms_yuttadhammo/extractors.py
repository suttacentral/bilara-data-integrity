import logging
from typing import Tuple

from lxml.etree import _Element, fromstring, tostring

log = logging.getLogger(__name__)


class YuttaExtractor:
    @classmethod
    def get_html_from_xml(cls, xml_string: str) -> str:
        data = fromstring(xml_string).xpath("/xml/data")[0]
        html: str = data.xpath(".//text()")[0]
        return html

    @classmethod
    def get_page_from_xml(cls, xml_string: str) -> _Element:
        html = cls.get_html_from_xml(xml_string=xml_string)
        html = html.replace("class=b", 'class="b"')
        log.info(html)
        return fromstring(html)

    @classmethod
    def get_ms_msdiv(cls, paragraph: _Element) -> "Tuple[PaliMsId, PaliMsDivId]":
        a_ms = paragraph.xpath("./a[@class='ms']")[0]
        ms_id = PaliMsId.from_xml_id(a_ms.get("id", ""))
        msdiv_id = PaliMsDivId("")
        try:
            a_msdiv = paragraph.xpath("./a[@class='msdiv']")[0]
            msdiv_id = PaliMsDivId(a_msdiv.get("id", "").strip())
        except IndexError:
            log.trace("No msdiv if for ms: '%s'", ms_id)
        return ms_id, msdiv_id

    @classmethod
    def get_verse(cls, paragraph: _Element) -> "PaliVerse":
        text = paragraph.xpath("./text()")
        text = text[0] if text else ""
        versus = PaliVerse(text.strip())
        return versus

    @classmethod
    def clean_html(cls, cleaned_html: str) -> str:
        root = cls.get_page_from_html(html=cleaned_html)
        b = root.xpath("//div[@class='b']")
        tn = root.xpath("//div[@class='tn']")
        elems_to_remove = [*b, *tn]
        for e in elems_to_remove:
            e.getparent().remove(e)
        out_html = tostring(root, pretty_print=True, method="html").decode("utf-8")
        out_html = html.unescape(out_html)
        return out_html
