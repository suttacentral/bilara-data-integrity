class SuttaError(Exception):
    pass


class SkipFileError(SuttaError):
    pass


class SegmentIdError(SuttaError):
    pass


class NoTokensError(SuttaError):
    pass


class MsIdError(SuttaError):
    pass


class PaliXmlIdError(SuttaError):
    pass


class SCReferenceError(SuttaError):
    pass


class MultipleIdFoundError(SCReferenceError):
    pass
