import html
import logging
from typing import List

from lxml.etree import _Element, fromstring, tostring

from sutta_processor.shared.exceptions import MultipleIdFoundError

log = logging.getLogger(__name__)


class YuttaExtractor:
    @classmethod
    def get_html_from_xml(cls, xml_string: str) -> str:
        data = fromstring(xml_string).xpath("/xml/data")[0]
        html: str = data.xpath(".//text()")[0]
        return html

    @classmethod
    def get_page_from_html(cls, html: str) -> _Element:
        return fromstring(html.replace("<br>", "<br/>"))

    @classmethod
    def get_id_nodes(cls, page: _Element) -> List[_Element]:
        id_nodes = page.xpath("//div[(@class='q' or @class='CENTER') and @id]")
        return id_nodes

    @classmethod
    def get_ms_id(cls, node: _Element) -> str:
        yutta_id: List[str] = node.xpath("./@id")
        if len(yutta_id) > 1:
            raise MultipleIdFoundError(f"Extracted ids: {yutta_id}")
        return yutta_id[0]

    @classmethod
    def get_verse(cls, node: _Element) -> str:
        return ""

    def get_verse2(cls, paragraph: _Element) -> "PaliVerse":
        text = paragraph.xpath("./text()")
        text = text[0] if text else ""
        versus = PaliVerse(text.strip())
        return versus

    @classmethod
    def clean_html(cls, cleaned_html: str) -> str:
        root = cls.get_page_from_html(html=cleaned_html)
        b = root.xpath("//div[@class='b']")
        tn = root.xpath("//div[@class='tn']")
        for e in [*b, *tn]:
            e.getparent().remove(e)
        out_html = tostring(root, pretty_print=True, method="html").decode("utf-8")
        out_html = html.unescape(out_html)
        return out_html
