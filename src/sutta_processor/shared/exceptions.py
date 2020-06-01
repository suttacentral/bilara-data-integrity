class SuttaError(Exception):
    pass


class SkipFileError(SuttaError):
    pass


class SegmentIdError(SuttaError):
    pass


class NoTokensError(SuttaError):
    pass


class IdError(SuttaError):
    pass


class ScIdError(IdError):
    pass


class PtsPliError(IdError):
    pass


class PtsCsError(IdError):
    pass


class MsIdError(IdError):
    pass


class PaliXmlIdError(IdError):
    pass


class SCReferenceError(SuttaError):
    pass


class MultipleIdFoundError(SCReferenceError):
    pass
