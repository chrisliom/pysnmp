"""
   Package exception classes.

   Written by Ilya Etingof <ilya@glas.net>, 2001, 2002.
"""   
from pysnmp import error

class SmiError(error.PySnmpError):
    """Base class for SMI sub-package exceptions
    """
    pass

# Common exceptions

class BadArgumentError(SmiError):
    """Malformed argument
    """
    pass

class NotImplementedError(SmiError):
    """Feature not implemented
    """
    pass

class NotImplementedError(SmiError):
    """Feature not implemented
    """
    pass
