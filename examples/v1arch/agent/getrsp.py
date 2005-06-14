"""Command Responder Application (RESPONSE PDU)"""
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram.udp import UdpSocketTransport
from pyasn1.codec.ber import encoder, decoder
from pysnmp.proto import api

def cbFun(tspDsp, transportDomain, transportAddress, wholeMsg):
    while wholeMsg:
        reqVer = api.decodeMessageVersion(wholeMsg)
        pMod = api.protoModules[reqVer]        
        reqMsg, wholeMsg = decoder.decode(
            wholeMsg, asn1Spec=pMod.Message(),
            )
        print 'Message version %s %s:%s: ' % (
            reqVer, transportDomain, transportAddress
            )
        print reqMsg.prettyPrinter()
        rspMsg = pMod.apiMessage.getResponse(reqMsg)
        rspPDU = pMod.apiMessage.getPDU(rspMsg)        
        reqPDU = pMod.apiMessage.getPDU(reqMsg)        
        # Support only a single PDU type (but any proto version)
        if reqPDU.isSameTypeWith(pMod.GetRequestPDU()):
            # Produce response var-binds
            varBinds = []
            for oid, val in pMod.apiPDU.getVarBinds(reqPDU):
                print transportAddress, oid, val
                varBinds.append((oid, val))
            pMod.apiPDU.setVarBinds(rspPDU, varBinds)                
        else:
            # Report unsupported request type
            pMod.apiPDU.setErrorStatus(rspPDU, 'genErr')
            print 'unsupported request type'
        print rspMsg.prettyPrinter()            
        tspDsp.sendMessage(
            encoder.encode(rspMsg), transportDomain, transportAddress
            )
    return wholeMsg

dsp = AsynsockDispatcher(
    udp=UdpSocketTransport().openServerMode(('localhost', 1161))
    )
dsp.registerRecvCbFun(cbFun)
dsp.runDispatcher(liveForever=1)
