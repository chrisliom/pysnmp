from pysnmp.proto import error

__all__ = [ 'MessageProcessingModelError' ]

class MessageProcessingModelError(error.ProtoError): pass
