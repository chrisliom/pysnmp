# PDU v1/v2c two-way proxy
from pysnmp.proto import rfc3411, error
from pysnmp.proto.api import v1, v2c
from pysnmp.smi import exval
from pysnmp import debug

# 2.1.1

__v1ToV2ValueMap = {
    v1.Integer.tagSet: v2c.Integer32(),
    v1.OctetString.tagSet: v2c.OctetString(),
    v1.Null.tagSet: v2c.Null(),
    v1.ObjectIdentifier.tagSet: v2c.ObjectIdentifier(),
    v1.IpAddress.tagSet: v2c.IpAddress(),
    v1.Counter.tagSet: v2c.Counter32(),
    v1.Gauge.tagSet: v2c.Gauge32(),
    v1.TimeTicks.tagSet: v2c.TimeTicks(),
    v1.Opaque.tagSet: v2c.Opaque()
    }

__v2ToV1ValueMap = { # XXX do not re-create same-type items?
    v2c.Integer32.tagSet: v1.Integer(),
    v2c.OctetString.tagSet: v1.OctetString(),
    v2c.Null.tagSet: v1.Null(),
    v2c.ObjectIdentifier.tagSet: v1.ObjectIdentifier(),
    v2c.IpAddress.tagSet: v1.IpAddress(),
    v2c.Counter32.tagSet: v1.Counter(),
    v2c.Gauge32.tagSet: v1.Gauge(),
    v2c.TimeTicks.tagSet: v1.TimeTicks(),
    v2c.Opaque.tagSet: v1.Opaque()
    }

# PDU map

__v1ToV2PduMap = {
    v1.GetRequestPDU.tagSet: v2c.GetRequestPDU(),
    v1.GetNextRequestPDU.tagSet: v2c.GetNextRequestPDU(),
    v1.SetRequestPDU.tagSet: v2c.SetRequestPDU(),
    v1.GetResponsePDU.tagSet: v2c.ResponsePDU(),
    v1.TrapPDU.tagSet: v2c.SNMPv2TrapPDU()
    }

__v2ToV1PduMap = {
    v2c.GetRequestPDU.tagSet: v1.GetRequestPDU(),
    v2c.GetNextRequestPDU.tagSet: v1.GetNextRequestPDU(),
    v2c.SetRequestPDU.tagSet: v1.SetRequestPDU(),
    v2c.ResponsePDU.tagSet: v1.GetResponsePDU(),
    v2c.SNMPv2TrapPDU.tagSet: v1.TrapPDU(),
    v2c.GetBulkRequestPDU.tagSet: v1.GetNextRequestPDU() # 4.1.1
    }

__sysUpTime = (1,3,6,1,2,1,1,3)
__snmpTrapAddress = (1,3,6,1,6,3,18,1,3,0)
__snmpTrapOID = (1,3,6,1,6,3,1,1,4,1,0)
__snmpTrapEnterprise = (1,3,6,1,6,3,1,1,4,3,0)
try:
    import socket
    __agentAddress = v1.IpAddress(socket.gethostbyname(socket.gethostname()))
except:
    __agentAddress = v1.IpAddress('0.0.0.0')

# Trap map

__v1ToV2TrapMap = {
    0: (1,3,6,1,6,3,1,1,5,1),
    1: (1,3,6,1,6,3,1,1,5,2),
    2: (1,3,6,1,6,3,1,1,5,3),
    3: (1,3,6,1,6,3,1,1,5,4),
    4: (1,3,6,1,6,3,1,1,5,5),
    5: (1,3,6,1,6,3,1,1,5,6)
    }

__v2ToV1TrapMap = {
    (1,3,6,1,6,3,1,1,5,1): 0,
    (1,3,6,1,6,3,1,1,5,2): 1,
    (1,3,6,1,6,3,1,1,5,3): 2,
    (1,3,6,1,6,3,1,1,5,4): 3,
    (1,3,6,1,6,3,1,1,5,5): 4,
    (1,3,6,1,6,3,1,1,5,6): 5
    }

# 4.3

__v2ToV1ErrorMap = {
    0:  0,
    1:  1,
    5:  5,
    10: 3,
    9:  3,
    7:  3,
    8:  3,
    12: 3,
    6:  2,
    17: 2,
    11: 2,
    18: 2,
    13: 5,
    14: 5,
    15: 5,
    16: 2
    }

def v1ToV2(v1Pdu, origV2Pdu=None):
    pduType = v1Pdu.tagSet
    v2Pdu = __v1ToV2PduMap[pduType].clone()
    v2c.apiPDU.setDefaults(v2Pdu)

    debug.logger & debug.flagPrx and debug.logger('v1ToV2: v1Pdu %s' % v1Pdu.prettyPrint())
    
    v2VarBinds = []

    # 3.1
    if rfc3411.notificationClassPDUs.has_key(pduType):
        # 3.1.1
        sysUpTime = v1.apiTrapPDU.getTimeStamp(v1Pdu)

        # 3.1.2
        genericTrap = v1.apiTrapPDU.getGenericTrap(v1Pdu)
        if genericTrap == 6:
            snmpTrapOIDParam = v1.apiTrapPDU.getEnterprise(v1Pdu) + (0,) + \
                               (v1.apiTrapPDU.getSpecificTrap(v1Pdu),)

        # 3.1.3
        else:
            snmpTrapOIDParam = v2c.ObjectIdentifier(
                                   __v1ToV2TrapMap[genericTrap]
                               )

        v2VarBinds.append((__sysUpTime, sysUpTime))
        v2VarBinds.append((__snmpTrapOID, snmpTrapOIDParam))
        v2VarBinds.append(
            (__snmpTrapEnterprise, v1.apiTrapPDU.getEnterprise(v1Pdu))
            )

        # 3.1.4
        v2VarBinds.append(
            (__snmpTrapAddress, v1.apiTrapPDU.getAgentAddr(v1Pdu))
            )
        
        varBinds = v1.apiTrapPDU.getVarBinds(v1Pdu)
    else:
        varBinds = v1.apiPDU.getVarBinds(v1Pdu)
        
    # Translate Var-Binds
    for oid, v1Val in varBinds:
        # 2.1.1.11
        if v1Val.tagSet == v1.NetworkAddress.tagSet:
            v1Val = v1Val.getComponent()
        v2VarBinds.append(
            (oid, __v1ToV2ValueMap[v1Val.tagSet].clone(v1Val))
            )
        
    if rfc3411.responseClassPDUs.has_key(pduType):
        # 4.1.2.2.1&2
        errorStatus = int(v1.apiPDU.getErrorStatus(v1Pdu))
        errorIndex = int(v1.apiPDU.getErrorIndex(v1Pdu))
        if errorStatus == 2: # noSuchName
            if origV2Pdu.tagSet == v2c.GetNextRequestPDU.tagSet:
                v2VarBinds[errorIndex-1] = (
                    v2VarBinds[errorIndex-1][0], exval.endOfMib
                    )
            else:
                v2VarBinds[errorIndex-1] = (
                    v2VarBinds[errorIndex-1][0], exval.noSuchObject
                    )
        else: # one-to-one mapping
            v2c.apiPDU.setErrorStatus(v2Pdu, errorStatus)
            v2c.apiPDU.setErrorIndex(v2Pdu, errorIndex)

        # 4.1.2.1 --> no-op

    if not rfc3411.notificationClassPDUs.has_key(pduType):
        v2c.apiPDU.setRequestID(v2Pdu, long(v1.apiPDU.getRequestID(v1Pdu)))

    v2c.apiPDU.setVarBinds(v2Pdu, v2VarBinds)

    debug.logger & debug.flagPrx and debug.logger('v1ToV2: v2Pdu %s' % v2Pdu.prettyPrint())
        
    return v2Pdu

def v2ToV1(v2Pdu, origV1Pdu=None):
    debug.logger & debug.flagPrx and debug.logger('v2ToV1: v2Pdu %s' % v2Pdu.prettyPrint())
    
    pduType = v2Pdu.tagSet
    
    v1Pdu = __v2ToV1PduMap[pduType].clone()

    v2VarBinds = v2c.apiPDU.getVarBinds(v2Pdu)
    v1VarBinds = []

    if rfc3411.notificationClassPDUs.has_key(pduType):
        v1.apiTrapPDU.setDefaults(v1Pdu)
    else:
        v1.apiPDU.setDefaults(v1Pdu)
        
    # 3.2
    if rfc3411.notificationClassPDUs.has_key(pduType):
        # 3.2.1
        (snmpTrapOID, snmpTrapOIDParam) = v2VarBinds[1]
        if snmpTrapOID != __snmpTrapOID:
            raise error.ProtocolError('Second OID not snmpTrapOID')

        if __v2ToV1TrapMap.has_key(snmpTrapOIDParam):
            for oid, val in v2VarBinds:
                if oid == __snmpTrapEnterprise:
                    v1.apiTrapPDU.setEnterprise(v1Pdu, val)
                    break
            else:
                # snmpTraps
                v1.apiTrapPDU.setEnterprise(v1Pdu, (1, 3, 6, 1, 6, 3, 1, 1, 5))
        else:
            if snmpTrapOIDParam[-2] == 0:
                v1.apiTrapPDU.setEnterprise(v1Pdu, snmpTrapOIDParam[:-2])
            else:
                v1.apiTrapPDU.setEnterprise(v1Pdu, snmpTrapOIDParam[:-1])

        # 3.2.2
        for oid, val in v2VarBinds:
            # snmpTrapAddress
            if oid == __snmpTrapAddress:
                v1.apiTrapPDU.setAgentAddr(v1Pdu, val)
                break
        else:
            v1.apiTrapPDU.setAgentAddr(v1Pdu, __agentAddress)

        # 3.2.3
        if __v2ToV1TrapMap.has_key(snmpTrapOIDParam):
            v1.apiTrapPDU.setGenericTrap(v1Pdu, __v2ToV1TrapMap[snmpTrapOIDParam])
        else:
            v1.apiTrapPDU.setGenericTrap(v1Pdu, 6)

        # 3.2.4
        if __v2ToV1TrapMap.has_key(snmpTrapOIDParam):
            v1.apiTrapPDU.setSpecificTrap(v1Pdu, 0)
        else:
            v1.apiTrapPDU.setSpecificTrap(v1Pdu, snmpTrapOIDParam[-1])

        # 3.2.5
        v1.apiTrapPDU.setTimeStamp(v1Pdu, v2VarBinds[0][1])

        __v2VarBinds = []
        for oid, val in v2VarBinds[2:]:
            if __v2ToV1TrapMap.has_key(oid) or \
                   oid in (__sysUpTime, __snmpTrapAddress,
                           __snmpTrapEnterprise):
                continue
            __v2VarBinds.append((oid, val))
        v2VarBinds = __v2VarBinds;
        
        # 3.2.6 --> done below

    if rfc3411.responseClassPDUs.has_key(pduType):
        idx = len(v2VarBinds)-1
        while idx >= 0:
            # 4.1.2.1
            oid, val = v2VarBinds[idx]
            if v2c.Counter64.tagSet == val.tagSet:
                if origV1Pdu.tagSet == v1.GetRequestPDU.tagSet:
                    v1.apiPDU.setErrorStatus(v1Pdu, 2)
                    v1.apiPDU.setErrorIndex(v1Pdu, idx+1)
                    break
                elif origV1Pdu.tagSet == v1.GetNextRequestPDU.tagSet:
                    raise error.StatusInformation(idx=idx, pdu=v2Pdu)
                else:
                    raise error.ProtocolError('Counter64 on the way')

            # 4.1.2.2.1&2
            if exval.noSuchInstance.tagSet == val.tagSet or \
               exval.noSuchObject.tagSet == val.tagSet or \
               exval.endOfMib.tagSet == val.tagSet:
                v1.apiPDU.setErrorStatus(v1Pdu, 2)
                v1.apiPDU.setErrorIndex(v1Pdu, idx+1)
                
            idx = idx - 1

        # 4.1.2.3.1
        v2ErrorStatus = v2c.apiPDU.getErrorStatus(v2Pdu)
        if v2ErrorStatus:
            v1.apiPDU.setErrorStatus(
                v1Pdu, __v2ToV1ErrorMap[v2ErrorStatus]
                )
            v1.apiPDU.setErrorIndex(v1Pdu, v2c.apiPDU.getErrorIndex(v2Pdu))
            
    # Translate Var-Binds
    for oid, v2Val in v2VarBinds:
        v1VarBinds.append((oid, __v2ToV1ValueMap[v2Val.tagSet].clone(v2Val)))

    if rfc3411.notificationClassPDUs.has_key(pduType):
        v1.apiTrapPDU.setVarBinds(v1Pdu, v1VarBinds)
    else:
        v1.apiPDU.setVarBinds(v1Pdu, v1VarBinds)

        v1.apiPDU.setRequestID(
            v1Pdu, v2c.apiPDU.getRequestID(v2Pdu)
            )

    debug.logger & debug.flagPrx and debug.logger('v2ToV1: v1Pdu %s' % v1Pdu.prettyPrint())
        
    return v1Pdu
