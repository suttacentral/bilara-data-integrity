import html
import logging
from collections import Counter
from typing import List

from lxml.etree import _Element, fromstring, tostring

from sutta_processor.shared.exceptions import MultipleIdFoundError

log = logging.getLogger(__name__)


class YuttaExtractor:
    c = Counter()

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
        search_class = (
            "@class='q' or "
            "@class='CENTER' or "
            "@class='ENDH3' or "
            "@class='SUMMARY' or "
            "@class='ENDBOOK'"
        )
        id_nodes = page.xpath(f"//div[({search_class}) and @id]")
        return id_nodes

    @classmethod
    def get_ms_id(cls, node: _Element) -> str:
        yutta_id: List[str] = node.xpath("./@id")
        if len(yutta_id) > 1:
            raise MultipleIdFoundError(f"Extracted ids: {yutta_id}")
        return yutta_id[0]

    @classmethod
    def get_verse(cls, node: _Element) -> str:
        handlers = {
            3: cls.handle_len3_verse,
            5: cls.handle_len5_verse,
            7: cls.handle_len7_verse,
        }
        text_parts = node.xpath(".//text()")
        cb = handlers.get(len(text_parts), cls.handle_len7_verse)
        versus = cb(text_parts=text_parts)
        return versus

    @classmethod
    def get_str_from_parts(cls, parts: List[str]) -> str:
        """ Used by handlers to combine parts. """
        return " ".join(parts)

    @classmethod
    def clean_up_part(cls, part: str) -> str:
        """ Clean up things that go to parts. """
        return part.replace("\xa0", " ")

    @classmethod
    def handle_len3_verse(cls, text_parts: List[str]) -> str:
        """
        :param text_parts: ['\n', '7', '(Pañhāvāraṃ vitthāretabbaṃ.)']
        :return:
        """
        out = []
        for part in text_parts:
            part = part.strip()
            if not part or part.isnumeric():
                continue
            out.append(cls.clean_up_part(part))
        return cls.get_str_from_parts(parts=out)

    @classmethod
    def handle_len5_verse(cls, text_parts: List[str]) -> str:
        """
        :param text_parts: ['\n', '1143', 'Evaṃ duvidhena rūpasaṅgaho.',
                            ' Sukhumarūpadukaṃ.', ' Dukaṃ.']
        :return:
        """
        out = []
        for part in text_parts:
            part = part.strip()
            if not part or part.isnumeric():
                continue
            out.append(cls.clean_up_part(part))
        return cls.get_str_from_parts(parts=out)

    @classmethod
    def handle_len7_verse(cls, text_parts: List[str]) -> str:
        """
        :param text_parts: ['\n', '1143', 'Evaṃ duvidhena rūpasaṅgaho.',
                            ' Sukhumarūpadukaṃ.', ' Dukaṃ.']
        :return:
        """
        out = []
        for part in text_parts:
            part = part.strip()
            if not part or part.isnumeric():
                continue
            if part.replace(".", "").replace("--", "").isnumeric():
                continue
            out.append(cls.clean_up_part(part))
        return cls.get_str_from_parts(parts=out)

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
