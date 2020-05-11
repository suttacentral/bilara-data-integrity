from abc import ABC

import attr


@attr.s(frozen=True, auto_attribs=True)
class BaseRootAggregate(ABC):
    _LOAD_INFO = "* [%s] Loaded '%s' UIDs"
    _PROCESS_INFO = (
        "* [%s] Processed: '%s' files. good: '%s', bad: '%s'. Failed ratio: %.2f%%"
    )
