"""
   An implementation of high-level API to SNMP v.1 message PDU objects
   (RFC1157)

   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'GetRequestPduMixIn', 'GetNextRequestPduMixIn',
            'SetRequestPduMixIn', 'GetResponsePduMixIn',
            'ResponsePduMixIn', 'TrapPduMixIn', 'MessageMixIn',
            'registerMixIns' ]

from pysnmp.proto import rfc1155, rfc1157
from pysnmp.proto.api import error

class RequestPduMixIn:
    def apiAlphaGetRequestId(self): return self['request_id']
    def apiAlphaSetRequestId(self, value): self['request_id'].set(value)
    def apiAlphaGetVarBind(self):
        outVars = []
        for varBind in self['variable_bindings']:
            outVars.append((varBind['name'],
                            varBind['value'].values()[0].values()[0]))
        return outVars
    
    def apiAlphaSetVarBind(self, inVars):
        varBindList = rfc1157.VarBindList()
        for inVar in inVars:
            try:
                (name, value) = inVar
            except ValueError:
                raise error.BadArgumentError('A [(name, value)] style arg expected by %s: %s' % (self.__class__.__name__, repr(inVar)))

            # Default to empty payload
            if value is None:
                value = rfc1155.Null()

            # Handle IP address
            if isinstance(value, rfc1155.IpAddress):
                value = rfc1155.NetworkAddress(addr=value)

            for comp in rfc1155.SimpleSyntax.choiceComponents:
                if isinstance(value, comp):
                    varBindList.append(rfc1157.VarBind(name=rfc1155.ObjectName(name), value=rfc1155.ObjectSyntax(simple=rfc1155.SimpleSyntax(t=value))))
                    break
            else:
                for comp in rfc1155.ApplicationSyntax.choiceComponents:
                    if isinstance(value, comp):
                        varBindList.append(rfc1157.VarBind(name=rfc1155.ObjectName(name), value=rfc1155.ObjectSyntax(simple=rfc1155.ApplicationSyntax(t=value))))
                        break
                else:
                    raise error.BadArgumentError('Unknown value type %s at %s' % (repr(value), self.__class__.__name__))
            
        self['variable_bindings'] = varBindList
    
# Request PDU mix-ins
class GetRequestPduMixIn(RequestPduMixIn): pass
class GetNextRequestPduMixIn(RequestPduMixIn): pass
class SetRequestPduMixIn(RequestPduMixIn): pass

class GetResponsePduMixIn(RequestPduMixIn):
    def apiAlphaGetErrorStatus(self): return self['error_status']
    def apiAlphaSetErrorStatus(self, value): self['error_status'].set(value)
    def apiAlphaGetErrorIndex(self): return self['error_index']
    def apiAlphaSetErrorIndex(self, value): self['error_index'].set(value)

# A v2c-style alias
ResponsePduMixIn = GetResponsePduMixIn

class TrapPduMixIn(RequestPduMixIn):
    def apiAlphaGetEnterprise(self):
        return self['enterprise']
    def apiAlphaSetEnterprise(self, value):
        self['enterprise'].set(value)
    def apiAlphaGetAgentAddr(self):
        return self['agent_addr']['internet']
    def apiAlphaSetAgentAddr(self, value):
        self['agent_addr']['internet'].set(value)
    def apiAlphaGetGenericTrap(self):
        return self['generic_trap']
    def apiAlphaSetGenericTrap(self, value):
        self['generic_trap'].set(value)
    def apiAlphaGetSpecificTrap(self):
        return self['specific_trap']
    def apiAlphaSetSpecificTrap(self, value):
        self['specific_trap'].set(value)
    def apiAlphaGetTimeStamp(self):
        return self['time_stamp']
    def apiAlphaSetTimeStamp(self, value):
        self['time_stamp'].set(value)

class MessageMixIn:
    def apiAlphaGetVersion(self): return self['version']
    def apiAlphaGetCommunity(self): return self['community']
    def apiAlphaSetCommunity(self, value): self['community'].set(value)
    def apiAlphaGetPdu(self): return self['pdu'].values()[0]
    def apiAlphaSetPdu(self, value): self['pdu'][None] = value

def mixIn():
    """Register this module's mix-in classes at their bases
    """
    mixInComps = [ (rfc1157.GetRequestPdu, GetRequestPduMixIn),
                   (rfc1157.GetNextRequestPdu, GetNextRequestPduMixIn),
                   (rfc1157.SetRequestPdu, SetRequestPduMixIn),
                   (rfc1157.GetResponsePdu, GetResponsePduMixIn),
                   (rfc1157.TrapPdu, TrapPduMixIn),
                   (rfc1157.Message, MessageMixIn) ]

    for (baseClass, mixIn) in mixInComps:
        if mixIn not in baseClass.__bases__:
            baseClass.__bases__ = (mixIn, ) + baseClass.__bases__
