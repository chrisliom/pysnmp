"""Notification Receiver Application (TRAP PDU)"""
from pysnmp import setApiVersion
setApiVersion('v4')
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram.udp import UdpSocketTransport
from pysnmp.proto import omni

def cbFun(tspDsp, transportDomain, transportAddress, wholeMsg):
    metaReq = omni.MetaMessage()
    while wholeMsg:
        wholeMsg = metaReq.decode(wholeMsg)
        req = metaReq.omniGetCurrentComponent()

        reportStr = '%s (version ID %s) from %s:%s:\n' % (
            req.omniGetPdu().omniGetPduType(),
            req.omniGetProtoVersionId(), transportDomain, transportAddress
            )
        
        if req.omniGetPdu().omniGetPduType() == omni.trapPduType:
            pdu = req.omniGetPdu()
            if req.omniGetProtoVersionId() == omni.protoVersionId1:
                print reportStr, \
                      'Enterprise: %s\n' % pdu.omniGetEnterprise(),\
                'Agent Address: %s\n' % pdu.omniGetAgentAddr(),\
                      'Generic Trap: %s\n' % pdu.omniGetGenericTrap(),\
                      'Specific Trap: %s\n' % pdu.omniGetSpecificTrap(),\
                      'Uptime: %s\n' % pdu.omniGetTimeStamp(),\
                      'Var-binds:'
            for varBind in pdu.omniGetVarBindList():
                print varBind.omniGetOidVal()
        else:
            print reportStr + 'unsupported request type'
    return wholeMsg

dsp = AsynsockDispatcher(
    udp=UdpSocketTransport().openServerMode(('localhost', 1162))
    )
dsp.registerRecvCbFun(cbFun)
dsp.runDispatcher(liveForever=1)
