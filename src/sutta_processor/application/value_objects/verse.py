from abc import ABC
from typing import Tuple


class RawVerse(str):
    def __new__(cls, content: str):
        return super().__new__(cls, content)


class BaseVerse(ABC, str):
    @property
    def tokens(self) -> Tuple[str]:
        from sutta_processor.application.check_service.tokenizer import VersetTokenizer

        tokens = VersetTokenizer.get_tokens(txt=self)
        return tokens


class Verse(BaseVerse):
    def __new__(cls, content: str):
        return super().__new__(cls, content)


class HtmlVerse(BaseVerse):
    def __new__(cls, content: str):
        return super().__new__(cls, content)


class MsVerse(BaseVerse):
    def __new__(cls, content: str):
        return super().__new__(cls, content)
