from abc import ABC
from collections import namedtuple

from sutta_processor.shared.exceptions import NoTokensError


class RawVerse(str):
    def __new__(cls, content: str):
        return super().__new__(cls, content)


class VerseTokens(tuple):
    HEAD_KEY_LEN = 3

    HeadKey = namedtuple("HeadKey", "a b c", defaults=("EMPTY",) * HEAD_KEY_LEN)

    def __new__(cls, *a, **kw):
        tokens = super().__new__(cls, *a, **kw)
        if not tokens:
            raise NoTokensError(f"No tokens from args: '{a}', kwargs: '{kw}'")
        return tokens

    def is_subverse(self, other: "VerseTokens") -> bool:
        return self == other

    @property
    def head_key(self) -> HeadKey:
        if len(self) > self.HEAD_KEY_LEN:
            return self.HeadKey(*self[: self.HEAD_KEY_LEN])
        else:
            return self.HeadKey(*self[-self.HEAD_KEY_LEN :])


class BaseVerse(ABC, str):
    @property
    def tokens(self) -> VerseTokens:
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
