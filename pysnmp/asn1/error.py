"""
   Package exception classes.

   Written by Ilya Etingof <ilya@glas.net>, 2001, 2002.
"""   
from pysnmp import error

class Asn1Error(error.PySnmpError):
    """Base class for asn1 sub-package exceptions
    """
    pass

# Common exceptions

class BadArgumentError(Asn1Error):
    """Malformed argument
    """
    pass

class ValueConstraintError(Asn1Error):
    """Assigned value does not fit data type
    """
    pass

class ObjectTypeError(Asn1Error):
    """Wrong object type for operation
    """
    pass
