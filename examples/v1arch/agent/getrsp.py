"""Command Responder Application (GET PDU)"""
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram.udp import UdpSocketTransport
from pysnmp.proto.api import alpha

def cbFun(tspDsp, transportDomain, transportAddress, wholeMsg):
    metaReq = alpha.MetaMessage()
    while wholeMsg:
        wholeMsg = metaReq.decode(wholeMsg)
        req = metaReq.apiAlphaGetCurrentComponent()

        # Build response from request object
        rsp = req.apiAlphaReply()

        reportStr = '%s (version ID %s) from %s:%s: ' % (
            req.apiAlphaGetPdu().apiAlphaGetPduType(),
            req.apiAlphaGetProtoVersionId(),
            transportDomain, transportAddress
            )
    
        # Support only a single PDU type (but any proto version)
        if req.apiAlphaGetPdu().apiAlphaGetPduType() == alpha.getRequestPduType:
            # Produce response var-binds
            varBinds = []
            for varBind in req.apiAlphaGetPdu().apiAlphaGetVarBindList():
                oid, val = varBind.apiAlphaGetOidVal()
                version = val.apiAlphaGetProtoVersionId()
                val = alpha.protoVersions[version].OctetString(
                    '%s %s = %s' %  (reportStr, oid, val)
                    )
                varBinds.append((oid, val))
            apply(rsp.apiAlphaGetPdu().apiAlphaSetVarBindList, varBinds)
        else:
            # Report unsupported request type
            rsp.apiAlphaGetPdu().apiAlphaSetErrorStatus(5)
            print reportStr + 'unsupported request type'

    tspDsp.sendMessage(rsp.berEncode(), transportDomain, transportAddress)
    return wholeMsg

dsp = AsynsockDispatcher(
    udp=UdpSocketTransport().openServerMode(('localhost', 1161))
    )
dsp.registerRecvCbFun(cbFun)
dsp.runDispatcher(liveForever=1)
