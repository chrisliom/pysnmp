"""An implementation of high-level API to SNMP v2c message & PDU
   objects (RFC1905)
"""
from pysnmp.proto import rfc1905
from pysnmp.proto.omni import rfc1157, error

class VarBindMixIn(rfc1157.VarBindMixIn): pass

class PduMixInBase(rfc1157.PduMixInBase):
    def omniSetVarBindList(self, *varBinds):
        varBindList = self['variable_bindings']
        idx = 0
        for varBind in varBinds:
            if isinstance(varBind, rfc1905.VarBind):
                varBindList[idx] = varBind
            else:
                if len(varBindList) <= idx:
                    varBindList.append(varBindList.componentFactoryBorrow())
                varBindList[idx].omniSetOidVal(varBind)
            idx = idx + 1
        del varBindList[idx:]

class RequestPduMixIn(PduMixInBase, rfc1157.RequestPduMixIn):
    def omniReply(self, pdu=None):
        """Return initialized response PDU
        """
        if pdu is None:
            pdu = rfc1905.ResponsePdu()
        elif not isinstance(pdu, rfc1905.ResponsePdu):
            raise error.BadArgumentError(
                'Bad PDU type for reply %s at %s' %
                (pdu.__class__.__name__, self.__class__.__name__)
            )
        pdu.omniSetRequestId(self.omniGetRequestId())
        return pdu

    reply = omniReply

    def omniMatch(self, rspPdu):
        """Return true if response PDU matches this ours"""
        if not isinstance(rspPdu, rfc1905.ResponsePdu):
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
class InformRequestPduMixIn(RequestPduMixIn): pass
class ReportPduMixIn(PduMixInBase): pass
class SnmpV2TrapPduMixIn(PduMixInBase): pass

class ResponsePduMixIn(RequestPduMixIn, rfc1157.GetResponsePduMixIn):
    def omniGetEndOfMibIndices(self):
        indices = []; idx = 0
        for varBind in self.omniGetVarBindList():
            oid, val = varBind.omniGetOidVal()
            if isinstance(val, rfc1905.EndOfMibView):
                indices.append(idx)
            idx = idx + 1
        indices.reverse()
        return indices

    def omniSetEndOfMibIndices(self, *indices):
        varBinds = self.omniGetVarBindList()
        for idx in indices:
            bindValue = varBinds[idx-1]['value']
            bindValue['endOfMibView'] = bindValue.componentFactoryBorrow('endOfMibView')

# A v1-style alias
GetResponsePduMixIn = ResponsePduMixIn
    
class GetBulkRequestPduMixIn(RequestPduMixIn):
    def omniGetNonRepeaters(self): return self['non_repeaters']
    def omniSetNonRepeaters(self, value): self['non_repeaters'].set(value)
    def omniGetMaxRepetitions(self): return self['max_repetitions']
    def omniSetMaxRepetitions(self, value):
        self['max_repetitions'].set(value)

    def omniGetTableIndices(self, rsp, *headerVars):
        nonRepeaters = self.omniGetNonRepeaters().get()
        N = min(nonRepeaters, len(self.omniGetVarBindList()))
        R = max(len(self.omniGetVarBindList())-N, 0)
        if R == 0:
            M = 0
        else:
            M = min(self.omniGetMaxRepetitions().get(), \
                    (len(rsp.omniGetVarBindList())-N)/R)
        if len(headerVars) < R + N:
            raise error.BadArgumentError('Short table header')                
        endOfMibIndices = rsp.omniGetEndOfMibIndices()
        varBindList = rsp.omniGetVarBindList()        
        varBindRows = []; varBindTable = [ varBindRows ]
        for idx in range(N):
            if idx in endOfMibIndices:
                varBindRows.append(-1)
                continue
            oid, val = varBindList[idx].omniGetOidVal()
            # XXX isaprefix rename
            if not headerVars[idx].isaprefix(oid):
                varBindRows.append(-1)
                continue
            varBindRows.append(idx)
        for rowIdx in range(M):
            if len(varBindTable) < rowIdx+1:
                varBindTable.append([])
            varBindRow = varBindTable[-1]
            for colIdx in range(R):
                while rowIdx and len(varBindRow) < N:
                    varBindRow.append(varBindTable[-2][colIdx])
                if len(varBindRow) < colIdx+N+1:
                    varBindRow.append(-1)
                idx = N + rowIdx*R + colIdx
                oid, val = varBindList[idx].omniGetOidVal()
                if headerVars[colIdx+N].isaprefix(oid):
                    varBindRow[-1] = idx
        return varBindTable

class MessageMixIn(rfc1157.MessageMixIn):
    def omniReply(self, rsp=None):
        """Return initialized response message
        """
        if rsp is None:
            rsp = rfc1905.Message()
            rsp.omniSetPdu(self.omniGetPdu().omniReply())
        else:
            self.omniGetPdu().omniReply(rsp.omniGetPdu())
        rsp.omniSetCommunity(self.omniGetCommunity())
        return rsp

    def omniMatch(self, rsp):
        """Return true if response message matches this request"""
        if not isinstance(rsp, rfc1905.Message):
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

mixInComps = [ (rfc1905.VarBind, VarBindMixIn),
               (rfc1905.GetRequestPdu, GetRequestPduMixIn),
               (rfc1905.GetNextRequestPdu, GetNextRequestPduMixIn),
               (rfc1905.SetRequestPdu, SetRequestPduMixIn),
               (rfc1905.ResponsePdu, ResponsePduMixIn),
               (rfc1905.GetBulkRequestPdu, GetBulkRequestPduMixIn),
               (rfc1905.InformRequestPdu, InformRequestPduMixIn),
               (rfc1905.ReportPdu, ReportPduMixIn),
               (rfc1905.SnmpV2TrapPdu, SnmpV2TrapPduMixIn),
               (rfc1905.Message, MessageMixIn) ]

for baseClass, mixIn in mixInComps:
    if mixIn not in baseClass.__bases__:
        baseClass.__bases__ = (mixIn, ) + baseClass.__bases__
