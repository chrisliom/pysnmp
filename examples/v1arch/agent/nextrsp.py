"""Command Responder Application (GETNEXT PDU)"""
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram.udp import UdpSocketTransport
from pysnmp.proto import omni

mibInstVer = omni.protoVersions[omni.protoVersionId1]
mibInstr = [
    (mibInstVer.ObjectName((1,3,6,1,2,1,1,1)), 'OctetString', __doc__),
    (mibInstVer.ObjectName((1,3,6,1,2,1,1,3)), 'TimeTicks', 26011971)
    ]

def cbFun(tspDsp, transportDomain, transportAddress, wholeMsg):
    metaReq = omni.MetaMessage()
    while wholeMsg:
        wholeMsg = metaReq.berDecode(wholeMsg)
        req = metaReq.omniGetCurrentComponent()

        # Build response from request object
        rsp = req.omniReply()

        # Support only a single PDU type (but any proto version)
        if req.omniGetPdu().omniGetPduType() == \
               omni.getNextRequestPduType:
            # Produce response var-binds
            varBinds = []; errorIndex = -1
            for varBind in req.omniGetPdu().omniGetVarBindList():
                oid, val = varBind.omniGetOidVal()
                mibIdx = -1; errorIndex = errorIndex + 1
                # Search next OID to report
                for idx in range(len(mibInstr)):
                    if idx == 0:
                        if oid < mibInstr[idx][0]:
                            mibIdx = idx
                            break
                    else:
                        if oid >= mibInstr[idx-1][0] and oid < mibInstr[idx][0]:
                            mibIdx = idx
                            break
                else:
                    # Out of MIB
                    rsp.omniGetPdu().omniSetEndOfMibIndices(errorIndex)

                # Report value if OID is found
                if mibIdx != -1:
                    mibOid, mibVar, mibVal = mibInstr[mibIdx]                
                    ver = omni.protoVersions[rsp.omniGetProtoVersionId()]
                    if hasattr(ver, mibVar):
                        varBinds.append(
                            (ver.ObjectName(mibOid),
                             getattr(ver, mibVar)(mibVal))
                            )
                        continue
                    else:
                        # Variable not available over this proto version
                        rsp.omniGetPdu().omniSetErrorIndex(errorIndex)
                        rsp.omniGetPdu().omniSetErrorStatus(5)

                varBinds.append((oid, val))
            apply(rsp.omniGetPdu().omniSetVarBindList, varBinds)
        else:
            # Report unsupported request type
            rsp.omniGetPdu().omniSetErrorStatus(5)
            print '%s (version ID %s) from %s:%s: unsupported request type' % (
                req.omniGetPdu().omniGetPduType(),
                req.omniGetProtoVersionId(),
                transportDomain, transportAddress
                )
    tspDsp.sendMessage(rsp.berEncode(), transportDomain, transportAddress)
    return wholeMsg

dsp = AsynsockDispatcher(
    udp=UdpSocketTransport().openServerMode(('localhost', 1161))
    )
dsp.registerRecvCbFun(cbFun)
dsp.runDispatcher(liveForever=1)
