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

from pysnmp.proto import rfc1902, rfc1905
from pysnmp.proto.api.alpha import rfc1157
from pysnmp.proto.api import error

class RequestPduMixIn(rfc1157.RequestPduMixIn):
    def apiAlphaGetVarBind(self):
        outVars = []
        for varBind in self['variable_bindings']:
            # The value in v2c var may appear at different levels
            value = varBind['value']
            while 1:
                if isinstance(value, rfc1902.Choice):
                    value = value.values()[0]
                else:
                    break
                
            outVars.append((varBind['name'], value))

        return outVars

    def apiAlphaSetVarBind(self, inVars):
        varBindList = rfc1905.VarBindList()
        for inVar in inVars:
            try:
                (name, value) = inVar
            except ValueError:
                raise error.BadArgumentError('A [(name, value)] style arg expected by %s: %s' % (self.__class__.__name__, repr(inVar)))

            # Default to empty payload
            if value is None: value = rfc1902.Null()

            for comp in rfc1905.BindValue.choiceComponents:
                if isinstance(value, comp):
                    varBindList.append(rfc1905.VarBind(name=rfc1902.ObjectName(name), value=rfc1905.BindValue(t=value)))
                    break
            else:
                for comp in rfc1902.SimpleSyntax.choiceComponents:
                    if isinstance(value, comp):
                        varBindList.append(rfc1905.VarBind(name=rfc1902.ObjectName(name), value=rfc1905.BindValue(syntax=rfc1902.ObjectSyntax(simple=rfc1902.SimpleSyntax(t=value)))))
                        break
                else:
                    for comp in rfc1902.ApplicationSyntax.choiceComponents:
                        if isinstance(value, comp):
                            varBindList.append(rfc1905.VarBind(name=rfc1902.ObjectName(name), value=rfc1905.BindValue(syntax=rfc1902.ObjectSyntax(app=rfc1902.ApplicationSyntax(t=value)))))
                            break
                    else:
                        raise error.BadArgumentError('Unknown value type %s at %s' % (repr(value), self.__class__.__name__))

        self['variable_bindings'] = varBindList

# Request PDU mix-ins
class GetRequestPduMixIn(RequestPduMixIn): pass
class GetNextRequestPduMixIn(RequestPduMixIn): pass
class SetRequestPduMixIn(RequestPduMixIn): pass
class InformRequestPduMixIn(RequestPduMixIn): pass
class ReportPduMixIn(RequestPduMixIn): pass
class SnmpV2TrapPduMixIn(RequestPduMixIn): pass

class ResponsePduMixIn(RequestPduMixIn):
    def apiAlphaGetErrorStatus(self): return self['error_status']
    def apiAlphaSetErrorStatus(self, value): self['error_status'].set(value)
    def apiAlphaGetErrorIndex(self): return self['error_index']
    def apiAlphaSetErrorIndex(self, value): self['error_index'].set(value)

# A v1-style alias
GetResponsePduMixIn = ResponsePduMixIn
    
class GetBulkRequestPduMixIn(RequestPduMixIn):
    def apiAlphaGetNonRepeaters(self): return self['non_repeaters']
    def apiAlphaSetNonRepeaters(self, value): self['non_repeaters'].set(value)
    def apiAlphaGetMaxRepetitions(self): return self['max_repetitions']
    def apiAlphaSetMaxRepetitions(self, value):
        self['max_repetitions'].set(value)

class MessageMixIn:
    def apiAlphaGetVersion(self): return self['version']
    def apiAlphaGetCommunity(self): return self['community']
    def apiAlphaSetCommunity(self, value): self['community'].set(value)
    def apiAlphaGetPdu(self): return self['pdu'].values()[0]
    def apiAlphaSetPdu(self, value): self['pdu'][None] = value

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
