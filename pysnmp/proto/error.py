"""
   Package exception classes.

   Written by Ilya Etingof <ilya@glas.net>, 2001, 2002.
"""   
from pysnmp import error

class ProtoError(error.PySnmpError):
    """Base class for snmp sub-package exceptions
    """
    pass

# Common exceptions

class BadArgumentError(ProtoError): pass
class NotImplementedError(ProtoError): pass

# SNMP v3 exceptions

class SnmpV3Error(ProtoError): pass
class CacheExpiredError(SnmpV3Error): pass
class InternalError(SnmpV3Error): pass
class MessageProcessingError(SnmpV3Error): pass
class CacheExpiredError(SnmpV3Error): pass
class RequestTimeout(SnmpV3Error): pass
