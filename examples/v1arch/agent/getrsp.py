"""Command Responder Application (GET PDU)"""
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram.udp import UdpSocketTransport
from pysnmp.proto import omni

def cbFun(tspDsp, transportDomain, transportAddress, wholeMsg):
    metaReq = omni.MetaMessage()
    while wholeMsg:
        wholeMsg = metaReq.decode(wholeMsg)
        req = metaReq.omniGetCurrentComponent()

        # Build response from request object
        rsp = req.omniReply()

        reportStr = '%s (version ID %s) from %s:%s: ' % (
            req.omniGetPdu().omniGetPduType(),
            req.omniGetProtoVersionId(),
            transportDomain, transportAddress
            )
    
        # Support only a single PDU type (but any proto version)
        if req.omniGetPdu().omniGetPduType() == omni.getRequestPduType:
            # Produce response var-binds
            varBinds = []
            for varBind in req.omniGetPdu().omniGetVarBindList():
                oid, val = varBind.omniGetOidVal()
                version = val.omniGetProtoVersionId()
                val = omni.protoVersions[version].OctetString(
                    '%s %s = %s' %  (reportStr, oid, val)
                    )
                varBinds.append((oid, val))
            apply(rsp.omniGetPdu().omniSetVarBindList, varBinds)
        else:
            # Report unsupported request type
            rsp.omniGetPdu().omniSetErrorStatus(5)
            print reportStr + 'unsupported request type'

    tspDsp.sendMessage(rsp.berEncode(), transportDomain, transportAddress)
    return wholeMsg

dsp = AsynsockDispatcher(
    udp=UdpSocketTransport().openServerMode(('localhost', 1161))
    )
dsp.registerRecvCbFun(cbFun)
dsp.runDispatcher(liveForever=1)
