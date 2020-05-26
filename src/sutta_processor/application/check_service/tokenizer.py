from typing import Callable, Tuple

from sutta_processor.application.value_objects.verse import VerseTokens


class VersetTokenizer:
    chars_list = set("""“”‘’"'.:;,?!*()—☑๐×☒""")
    skip_chars = {ch: None for ch in chars_list}
    skip_chars["…"] = " "

    @classmethod
    def translate(cls, txt: str) -> str:
        txt = txt.replace("**ti", " ti")
        return txt.translate(str.maketrans(cls.skip_chars))

    @classmethod
    def remove_numbers(cls, tokens: VerseTokens) -> VerseTokens:
        return VerseTokens(s for s in tokens if not s.isdigit())

    @classmethod
    def get_transform_callbacks(cls) -> Tuple[Callable]:
        callbacks = (cls.translate,)
        return callbacks

    @classmethod
    def get_tokens(cls, txt: str) -> VerseTokens:
        txt = txt.lower()
        for cb in cls.get_transform_callbacks():
            txt = cb(txt=txt)

        tokens = VerseTokens(txt.split())
        return tokens
