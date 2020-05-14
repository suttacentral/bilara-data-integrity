class SuttaError(Exception):
    pass


class SegmentIdError(SuttaError):
    pass


class MsIdError(SuttaError):
    pass


class PaliXmlIdError(SuttaError):
    pass


class SCReferenceError(SuttaError):
    pass


class MultipleIdFoundError(SCReferenceError):
    pass
