"""
   An implementation of high-level API to SNMP v.2c message PDU objects
   (RFC1905)

   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'GetRequestPduMixIn', 'GetNextRequestPduMixIn',
            'SetRequestPduMixIn', 'ResponsePduMixIn',
            'GetBulkRequestPduMixIn', 'InformRequestPduMixIn',
            'ReportPduMixIn', 'SnmpV2TrapPduMixIn', 'MessageMixIn',
            'registerMixIns' ]

from pysnmp.asn1.base import SimpleAsn1Object
from pysnmp.proto import rfc1905
from pysnmp.proto.api.alpha import rfc1157
from pysnmp.proto.api import error

class RequestPduMixIn(rfc1157.RequestPduMixIn):
    def apiAlphaGetVarBind(self):
        return map(lambda x: \
                   (x['name'], x['value'].getInnerComponent(SimpleAsn1Object)),
                   self['variable_bindings'])

# Request PDU mix-ins
class GetRequestPduMixIn(RequestPduMixIn): pass
class GetNextRequestPduMixIn(RequestPduMixIn): pass
class SetRequestPduMixIn(RequestPduMixIn): pass
class InformRequestPduMixIn(RequestPduMixIn): pass
class ReportPduMixIn(RequestPduMixIn): pass
class SnmpV2TrapPduMixIn(RequestPduMixIn): pass

class ResponsePduMixIn(RequestPduMixIn, rfc1157.GetResponsePduMixIn): pass

# A v1-style alias
GetResponsePduMixIn = ResponsePduMixIn
    
class GetBulkRequestPduMixIn(RequestPduMixIn):
    def apiAlphaGetNonRepeaters(self): return self['non_repeaters']
    def apiAlphaSetNonRepeaters(self, value): self['non_repeaters'].set(value)
    def apiAlphaGetMaxRepetitions(self): return self['max_repetitions']
    def apiAlphaSetMaxRepetitions(self, value):
        self['max_repetitions'].set(value)

class MessageMixIn(rfc1157.MessageMixIn): pass

def mixIn():
    """Register this module's mix-in classes at their bases
    """
    mixInComps = [ (rfc1905.GetRequestPdu, GetRequestPduMixIn),
                   (rfc1905.GetNextRequestPdu, GetNextRequestPduMixIn),
                   (rfc1905.SetRequestPdu, SetRequestPduMixIn),
                   (rfc1905.ResponsePdu, ResponsePduMixIn),
                   (rfc1905.GetBulkRequestPdu, GetBulkRequestPduMixIn),
                   (rfc1905.InformRequestPdu, InformRequestPduMixIn),
                   (rfc1905.ReportPdu, ReportPduMixIn),
                   (rfc1905.SnmpV2TrapPdu, SnmpV2TrapPduMixIn),
                   (rfc1905.Message, MessageMixIn) ]

    for (baseClass, mixIn) in mixInComps:
        if mixIn not in baseClass.__bases__:
            baseClass.__bases__ = (mixIn, ) + baseClass.__bases__
