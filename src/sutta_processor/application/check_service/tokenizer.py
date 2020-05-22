from typing import Callable, Tuple


class VersetTokenizer:
    chars_list = set("""“”‘’"'.:;,…?!*()—""")
    skip_chars = {ch: None for ch in chars_list}

    @classmethod
    def translate(cls, txt: str) -> str:
        return txt.translate(str.maketrans(cls.skip_chars))

    @classmethod
    def remove_numbers(cls, tokens: Tuple[str]) -> Tuple[str]:
        return tuple(s for s in tokens if not s.isdigit())

    @classmethod
    def get_transform_callbacks(cls) -> Tuple[Callable]:
        callbacks = (cls.translate,)
        return callbacks

    @classmethod
    def get_tokens(cls, txt: str) -> Tuple[str]:
        for cb in cls.get_transform_callbacks():
            txt = cb(txt=txt)

        tokens = tuple(txt.split())
        return tokens
