from pysnmp.proto import error

__all__ = [ 'SecurityModelError' ]

class SecurityModelError(error.ProtoError): pass
class BadArgumentError(SecurityModelError): pass
