"""Command Responder Application (GETNEXT PDU)"""
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram.udp import UdpSocketTransport
from pysnmp.proto.api import alpha

mibInstVer = alpha.protoVersions[alpha.protoVersionId1]
mibInstr = [
    (mibInstVer.ObjectName((1,3,6,1,2,1,1,1)), 'OctetString', __doc__),
    (mibInstVer.ObjectName((1,3,6,1,2,1,1,3)), 'TimeTicks', 26011971)
    ]

def cbFun(tspDsp, transportDomain, transportAddress, wholeMsg):
    metaReq = alpha.MetaMessage()
    while wholeMsg:
        wholeMsg = metaReq.berDecode(wholeMsg)
        req = metaReq.apiAlphaGetCurrentComponent()

        # Build response from request object
        rsp = req.apiAlphaReply()

        # Support only a single PDU type (but any proto version)
        if req.apiAlphaGetPdu().apiAlphaGetPduType() == \
               alpha.getNextRequestPduType:
            # Produce response var-binds
            varBinds = []; errorIndex = -1
            for varBind in req.apiAlphaGetPdu().apiAlphaGetVarBindList():
                oid, val = varBind.apiAlphaGetOidVal()
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
                    rsp.apiAlphaGetPdu().apiAlphaSetEndOfMibIndices(errorIndex)

                # Report value if OID is found
                if mibIdx != -1:
                    mibOid, mibVar, mibVal = mibInstr[mibIdx]                
                    ver = alpha.protoVersions[rsp.apiAlphaGetProtoVersionId()]
                    if hasattr(ver, mibVar):
                        varBinds.append(
                            (ver.ObjectName(mibOid),
                             getattr(ver, mibVar)(mibVal))
                            )
                        continue
                    else:
                        # Variable not available over this proto version
                        rsp.apiAlphaGetPdu().apiAlphaSetErrorIndex(errorIndex)
                        rsp.apiAlphaGetPdu().apiAlphaSetErrorStatus(5)

                varBinds.append((oid, val))
            apply(rsp.apiAlphaGetPdu().apiAlphaSetVarBindList, varBinds)
        else:
            # Report unsupported request type
            rsp.apiAlphaGetPdu().apiAlphaSetErrorStatus(5)
            print '%s (version ID %s) from %s:%s: unsupported request type' % (
                req.apiAlphaGetPdu().apiAlphaGetPduType(),
                req.apiAlphaGetProtoVersionId(),
                transportDomain, transportAddress
                )
    tspDsp.sendMessage(rsp.berEncode(), transportDomain, transportAddress)
    return wholeMsg

dsp = AsynsockDispatcher(
    udp=UdpSocketTransport().openServerMode(('localhost', 1161))
    )
dsp.registerRecvCbFun(cbFun)
dsp.runDispatcher(liveForever=1)
