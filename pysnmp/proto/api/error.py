"""
   Package exception classes.

   Written by Ilya Etingof <ilya@glas.net>, 2001-2003.
"""   
from pysnmp.proto import error

class ApiError(error.ProtoError):
    """Base class for api sub-package exceptions
    """
    pass

# Common exceptions

class BadArgumentError(ApiError):
    """Malformed argument
    """
    pass
