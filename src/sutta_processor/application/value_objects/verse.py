from abc import ABC
from collections import namedtuple

from sutta_processor.shared.exceptions import (
    MsIdError,
    NyaError,
    PtsCsError,
    PtsPliError,
    ScIdError,
)

from .uid import UID, BaseUID, MsId, Nya, PtsCs, PtsPli, ScID


class RawVerse(str):
    def __new__(cls, content: str):
        return super().__new__(cls, content)


class References(set):
    sc_id: ScID
    sc_id: PtsPli
    pts_cs: PtsCs
    nya: Nya

    def __init__(self, *a):
        """
        From root_reference: ('sc38, pts-vp-pli11, ms24Mn_38',)
        """
        sc_id = ""
        pts_pli = ""
        pts_cs = ""
        nya = ""
        if len(a) == 1:
            parts = set()
            ids = a[0]
            if isinstance(ids, str):
                if "," in ids:
                    ids = ids.split(",")
                else:
                    ids = [ids]
            for part in ids:
                part = BaseUID(part.strip())
                if not part:
                    continue
                try:
                    part = ScID(part)
                    if not sc_id:
                        # It might happen that there are several sc_ids in
                        # references. That will set the first as the reference
                        # eg. "mn10:34.1": "msdiv114, sc39, sc48,.." will set sc39
                        sc_id = part
                except ScIdError:
                    pass
                try:
                    part = PtsPli(part)
                    if not pts_pli:
                        # It might happen that there are several sc_ids in
                        # references. That will set the first as the reference
                        # eg. "mn10:34.1": "msdiv114, sc39, sc48,.." will set sc39
                        pts_pli = part
                except PtsPliError:
                    pass
                try:
                    part = PtsCs(part)
                    pts_cs = part
                except PtsCsError:
                    pass

                try:
                    part = Nya(part)

                    nya = part
                except NyaError:
                    pass
                try:
                    part = MsId(part)
                    pts_cs = part
                except MsIdError:
                    pass
                parts.add(part)
        else:
            parts = a
        super().__init__(parts)
        self.sc_id = sc_id
        self.pts_pli = pts_pli
        self.pts_cs = pts_cs
        self.nya = nya

    @property
    def data(self) -> str:
        return ", ".join(sorted(self))

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
