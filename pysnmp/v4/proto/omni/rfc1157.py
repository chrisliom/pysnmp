"""An implementation of high-level API to SNMP v1 message & PDU
   objects (RFC1157)
"""
from types import InstanceType
from pysnmp.proto import rfc1157
from pysnmp.proto.omni import error

class VarBindMixIn:
    def omniSetOidVal(self, (oid, val)):
        if oid is not None:
            self.omniSetSimpleComponent('name', oid)
        if val is not None:
            self['value'].omniSetTerminalValue(val)
        return self

    def omniGetOidVal(self):
        return (self['name'], self['value'].omniGetTerminalValue())

class PduMixInBase:
    def omniGetVarBindList(self): return self['variable_bindings']
    def omniSetVarBindList(self, *varBinds):
        varBindList = self['variable_bindings']
        idx = 0
        for varBind in varBinds:
            if isinstance(varBind, rfc1157.VarBind):
                varBindList[idx] = varBind
            else:
                if len(varBindList) <= idx:
                    varBindList.append(varBindList.componentFactoryBorrow())
                varBindList[idx].omniSetOidVal(varBind)
            idx = idx + 1
        del varBindList[idx:]

    def omniGetTableIndices(self, rsp, *headerVars):
        varBindList = rsp.omniGetVarBindList()
        if not varBindList:  # Shortcut for no-varbinds PDU
            return [ [ -1 ] * len(headerVars) ]
        if len(varBindList) != len(headerVars):
            raise error.BadArgumentError(
                'Unmatching table head & row size %s vs %s' %
                (len(headerVars), len(varBindList))
            )
        if not headerVars:
            raise error.BadArgumentError('Empty table')
        endOfMibIndices = rsp.omniGetEndOfMibIndices()
        varBindRows = []
        for idx in range(len(varBindList)):
            if idx in endOfMibIndices:
                varBindRows.append(-1)
                continue
            oid, val = varBindList[idx].omniGetOidVal()
            # XXX isaprefix rename
            if not headerVars[idx].isaprefix(oid):
                varBindRows.append(-1)
                continue
            varBindRows.append(idx)
        return [ varBindRows ]
            
class RequestPduMixIn(PduMixInBase):
    def omniGetRequestId(self): return self['request_id']
    def omniSetRequestId(self, value):
        self.omniSetSimpleComponent('request_id', value)
    def omniReply(self, pdu=None):
        """Return initialized response PDU
        """
        if pdu is None:
            pdu = rfc1157.GetResponsePdu()
        elif not isinstance(pdu, rfc1157.GetResponsePdu):
            raise error.BadArgumentError(
                'Bad PDU type for reply %s at %s' % 
                (pdu.__class__.__name__, self.__class__.__name__)
            )
        pdu.omniSetRequestId(self.omniGetRequestId().get())
        return pdu

    reply = omniReply

    def omniMatch(self, rspPdu):
        """Return true if response PDU matches this ours"""
        if not isinstance(rspPdu, rfc1157.GetResponsePdu):
            raise error.BadArgumentError(
                'Non-response PDU to match %s vs %s' %
                (self.__class__.__name__, str(rspPdu))
            )
        return self.omniGetRequestId() == rspPdu.omniGetRequestId()

    match = omniMatch

# Request PDU mix-ins
class GetRequestPduMixIn(RequestPduMixIn): pass
class GetNextRequestPduMixIn(RequestPduMixIn): pass
class SetRequestPduMixIn(RequestPduMixIn): pass

class GetResponsePduMixIn(RequestPduMixIn):
    def omniGetErrorStatus(self): return self['error_status']
    def omniSetErrorStatus(self, value):
        self.omniSetSimpleComponent('error_status', value)
    def omniGetErrorIndex(self):
        errorIndex = self['error_index']
        if errorIndex > len(self.omniGetVarBindList()):
            raise error.BadArgumentError(
                'Error index out of range (%s) at %s' %
                (errorIndex, self.__class__.__name__)
            )
        return errorIndex
    def omniSetErrorIndex(self, value):
        self.omniSetSimpleComponent('error_index', value)
    
    def omniGetEndOfMibIndices(self):
        if self.omniGetErrorStatus() == 2:
            return [ self.omniGetErrorIndex().get() - 1 ]
        return []

    def omniSetEndOfMibIndices(self, *indices):
        for idx in indices:
            self.omniSetErrorStatus(2)
            self.omniSetErrorIndex(idx+1)
            break

# XXX A v2c-style alias
ResponsePduMixIn = GetResponsePduMixIn

class TrapPduMixIn(PduMixInBase):
    def omniGetEnterprise(self):
        return self['enterprise']
    def omniSetEnterprise(self, value):
        self.omniSetSimpleComponent('enterprise', value)
    def omniGetAgentAddr(self):
        return self['agent_addr']['internet']
    def omniSetAgentAddr(self, value):
        # XXX this might need to be moved to some inner method
        if type(value) == InstanceType:
            self['agent_addr']['internet'] = value
        else:
            self['agent_addr']['internet'].set(value)
    def omniGetGenericTrap(self):
        return self['generic_trap']
    def omniSetGenericTrap(self, value):
        self.omniSetSimpleComponent('generic_trap', value)
    def omniGetSpecificTrap(self):
        return self['specific_trap']
    def omniSetSpecificTrap(self, value):
        self.omniSetSimpleComponent('specific_trap', value)
    def omniGetTimeStamp(self):
        return self['time_stamp']
    def omniSetTimeStamp(self, value):
        self.omniSetSimpleComponent('time_stamp', value)

class MessageMixIn:
    def omniGetVersion(self): return self['version']
    def omniGetCommunity(self): return self['community']
    def omniSetCommunity(self, value):
        self.omniSetSimpleComponent('community', value)
    def omniGetPdu(self):
        if len(self['pdu']):
            return self['pdu'].values()[0]
        raise error.BadArgumentError(
            'PDU not initialized at %s' %
            self.__class__.__name__
        )
    
    def omniSetPdu(self, value):
        self['pdu'].omniSetTerminalValue(value)

    def omniReply(self, rsp=None):
        """Return initialized response message"""
        if rsp is None:
            rsp = rfc1157.Message()
            rsp.omniSetPdu(self.omniGetPdu().omniReply())
        else:
            self.omniGetPdu().omniReply(rsp.omniGetPdu())
        rsp.omniSetCommunity(self.omniGetCommunity().get())
        return rsp

    def omniMatch(self, rsp):
        """Return true if response message matches this request"""
        if not isinstance(rsp, rfc1157.Message):
            raise error.BadArgumentError(
                'Non-message to match %s vs %s' %
                (self.__class__.__name__, str(rsp))
            )
        if self.omniGetCommunity() != rsp.omniGetCommunity():
            return
        return self.omniGetPdu().omniMatch(rsp.omniGetPdu())

    # Compatibility aliases
    reply = omniReply
    match = omniMatch
             
mixInComps = [ (rfc1157.VarBind, VarBindMixIn),
               (rfc1157.GetRequestPdu, GetRequestPduMixIn),
               (rfc1157.GetNextRequestPdu, GetNextRequestPduMixIn),
               (rfc1157.SetRequestPdu, SetRequestPduMixIn),
               (rfc1157.GetResponsePdu, GetResponsePduMixIn),
               (rfc1157.TrapPdu, TrapPduMixIn),
               (rfc1157.Message, MessageMixIn) ]

for baseClass, mixIn in mixInComps:
    if mixIn not in baseClass.__bases__:
        baseClass.__bases__ = (mixIn, ) + baseClass.__bases__
