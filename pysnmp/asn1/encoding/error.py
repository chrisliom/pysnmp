"""
   Package exception classes.

   Written by Ilya Etingof <ilya@glas.net>, 2001-2003.
"""   
from pysnmp.asn1 import error

class EncodingError(error.Asn1Error):
    """Base class for ber sub-package exceptions
    """
    pass
