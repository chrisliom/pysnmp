"""Notification Receiver Application (TRAP PDU)"""
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram.udp import UdpSocketTransport
from pyasn1.codec.ber import encoder, decoder
from pysnmp.proto import api

def cbFun(tspDsp, transportDomain, transportAddress, wholeMsg):
    while wholeMsg:
        reqVer = api.decodeMessageVersion(wholeMsg)
        pMod = api.protoModules[reqVer]        
        reqMsg, wholeMsg = decoder.decode(
            wholeMsg,
            asn1Spec=pMod.Message(),
            )
        print 'Message from %s:%s: ' % (
            transportDomain, transportAddress
            )
        print reqMsg.prettyPrinter()
        reqPDU = pMod.apiMessage.getPDU(reqMsg)
        if reqPDU.isSameTypeWith(pMod.TrapPDU()):
            if reqVer == api.protoVersion1:
                print 'Enterprise: %s' % (
                    pMod.apiTrapPDU.getEnterprise(reqPDU)
                    )
                print 'Agent Address: %s' % (
                    repr(pMod.apiTrapPDU.getAgentAddr(reqPDU))
                    )
                print 'Generic Trap: %s' % (
                    pMod.apiTrapPDU.getGenericTrap(reqPDU)
                    )
                print 'Specific Trap: %s' % (
                    pMod.apiTrapPDU.getSpecificTrap(reqPDU)
                    )
                print 'Uptime: %s' % (
                    pMod.apiTrapPDU.getTimeStamp(reqPDU)
                    )
                print 'Var-binds:'
                for varBind in pMod.apiTrapPDU.getVarBindList(reqPDU):
                    print pMod.apiVarBind.getOIDVal(varBind)
            else:
                print 'Var-binds:'
                for varBind in pMod.apiTrapPDU.getVarBindList(reqPDU):
                    print pMod.apiVarBind.getOIDVal(varBind)
        else:
            print 'unsupported request type'
    return wholeMsg

dsp = AsynsockDispatcher(
    udp=UdpSocketTransport().openServerMode(('localhost', 1162)) # 162
    )
dsp.registerRecvCbFun(cbFun)
dsp.runDispatcher(liveForever=1)
