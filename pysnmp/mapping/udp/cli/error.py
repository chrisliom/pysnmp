"""
   Package exception classes.

   Written by Ilya Etingof <ilya@glas.net>, 2001-2003.
"""   
from pysnmp.mapping.udp import error

class UdpCliError(error.SnmpOverUdpError):
    """Base class for sub-package exceptions
    """
    pass

# Common exceptions

class BadArgumentError(UdpCliError):
    """Malformed argument
    """
    pass
