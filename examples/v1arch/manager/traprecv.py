"""Notification Receiver Application (TRAP PDU)"""
from pysnmp import setApiVersion
setApiVersion('v4')
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram.udp import UdpSocketTransport
from pysnmp.proto.api import alpha

def cbFun(tspDsp, transportDomain, transportAddress, wholeMsg):
    metaReq = alpha.MetaMessage()
    while wholeMsg:
        wholeMsg = metaReq.decode(wholeMsg)
        req = metaReq.apiAlphaGetCurrentComponent()

        reportStr = '%s (version ID %s) from %s:%s:\n' % (
            req.apiAlphaGetPdu().apiAlphaGetPduType(),
            req.apiAlphaGetProtoVersionId(), transportDomain, transportAddress
            )
        
        if req.apiAlphaGetPdu().apiAlphaGetPduType() == alpha.trapPduType:
            pdu = req.apiAlphaGetPdu()
            if req.apiAlphaGetProtoVersionId() == alpha.protoVersionId1:
                print reportStr, \
                      'Enterprise: %s\n' % pdu.apiAlphaGetEnterprise(),\
                'Agent Address: %s\n' % pdu.apiAlphaGetAgentAddr(),\
                      'Generic Trap: %s\n' % pdu.apiAlphaGetGenericTrap(),\
                      'Specific Trap: %s\n' % pdu.apiAlphaGetSpecificTrap(),\
                      'Uptime: %s\n' % pdu.apiAlphaGetTimeStamp(),\
                      'Var-binds:'
            for varBind in pdu.apiAlphaGetVarBindList():
                print varBind.apiAlphaGetOidVal()
        else:
            print reportStr + 'unsupported request type'
    return wholeMsg

dsp = AsynsockDispatcher(
    udp=UdpSocketTransport().openServerMode(('localhost', 1162))
    )
dsp.registerRecvCbFun(cbFun)
dsp.runDispatcher(liveForever=1)
