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

from pysnmp.proto import rfc1157
from pysnmp.proto.api import error

class RequestPduMixIn:
    def apiAlphaGetRequestId(self): return self['request_id']
    def apiAlphaSetRequestId(self, value): self['request_id'].set(value)
    def apiAlphaGetVarBind(self):
        return map(lambda x: (x['name'], x['value'].values()[0].values()[0]),
                   self['variable_bindings'])

    # Initialize var-bindings. Try to re-use existing ones
    # (whenever possible) for better performance
    def apiAlphaSetVarBind(self, inVars):
        inVarsLen = len(inVars)
        varBindList = self['variable_bindings']
        if not hasattr(self, '_cachedVarBindLists'):
            self._cachedVarBindLists = { 0: varBindList }
        if not self._cachedVarBindLists.has_key(inVarsLen):
            self._cachedVarBindLists[inVarsLen] = apply(varBindList.__class__, map(lambda x, varBindList=varBindList: varBindList.protoComponent(), [0] * inVarsLen))
        varBindList = self._cachedVarBindLists[inVarsLen]
        idx = 0
        while idx < inVarsLen:
            try:
                (name, value) = inVars[idx]
            except ValueError:
                raise error.BadArgumentError('A [(name, value)] style arg expected by %s: %s' % (self.__class__.__name__, repr(inVars[idx])))

            varBind = varBindList[idx]

            varBind['name'].set(name)
            if not varBind['value'].setInnerComponent(value):
                raise error.BadArgumentError('Unexpected value type at %s: %s'\
                                             % (self.__class__.__name__, value))
            idx = idx + 1

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
