"""
   Package exception classes.

   Written by Ilya Etingof <ilya@glas.net>, 2001-2003.
"""   
from pysnmp.proto import error

class CliError(error.ProtoError):
    """Base class for snmp sub-package exceptions
    """
    pass

# Common exceptions

class BadArgumentError(CliError):
    """Malformed argument
    """
    pass

class NotImplementedError(CliError):
    """Feature not implemented
    """
    pass
