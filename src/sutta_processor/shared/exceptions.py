class SuttaError(Exception):
    pass


class PaliMsIdError(SuttaError):
    pass


class PaliXmlIdError(SuttaError):
    pass


class SCReferenceError(SuttaError):
    pass


class MultipleIdFoundError(SCReferenceError):
    pass
