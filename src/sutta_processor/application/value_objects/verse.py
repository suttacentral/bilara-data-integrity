from abc import ABC
from collections import namedtuple

from sutta_processor.shared.exceptions import ScIdError

from .uid import UID, ScID


class RawVerse(str):
    def __new__(cls, content: str):
        return super().__new__(cls, content)


class References(set):
    sc_id: ScID

    def __init__(self, *a):
        """
        From root_reference: ('sc38, pts-vp-pli11, ms24Mn_38',)
        From concordance: (['sc91', 'ms24Mn_767', 'cck26.187', 'bj33.276'],)
        """
        sc_id = ""
        if len(a) == 1:
            parts = set()
            ids = a[0]
            if isinstance(ids, str):
                if "," in ids:
                    ids = ids.split(",")
                else:
                    ids = [ids]
            for part in ids:
                part = part.strip()
                try:
                    part = ScID(part)
                    sc_id = part
                except ScIdError:
                    pass
                parts.add(part)
        else:
            parts = a
        super().__init__(parts)
        self.sc_id = sc_id

    @property
    def data(self) -> str:
        return ", ".join(sorted(self))


class ReferencesConcordance(References):
    uid: UID

    def __init__(self, *a, uid: UID):
        super().__init__(*a)
        self.uid = uid

    @property
    def data(self) -> list:
        return list(sorted(set(self)))


class VerseTokens(tuple):
    HEAD_KEY_LEN = 3

    HeadKey = namedtuple("HeadKey", "a b c", defaults=("EMPTY",) * HEAD_KEY_LEN)

    def __new__(cls, *a, **kw):
        tokens = super().__new__(cls, *a, **kw)
        # if not tokens:
        #     raise NoTokensError(f"No tokens from args: '{a}', kwargs: '{kw}'")
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
