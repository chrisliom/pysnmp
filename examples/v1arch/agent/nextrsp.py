"""Command Responder Application (GETNEXT PDU)"""
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram.udp import UdpSocketTransport
from pyasn1.codec.ber import encoder, decoder
from pysnmp.proto import api
import time, bisect

class SysDescr:
    name = (1,3,6,1,2,1,1,1)
    def __cmp__(self, other): return cmp(self.name, other)    
    def __call__(self, protoVer):
        return api.protoModules[protoVer].OctetString(
            'PySNMP example command responder %s' % __file__
            )

class Uptime:
    name = (1,3,6,1,2,1,1,3)
    birthday = time.time()
    def __cmp__(self, other): return cmp(self.name, other)
    def __call__(self, protoVer):
        return api.protoModules[protoVer].TimeTicks(
            (time.time()-self.birthday)*100
            )

mibInstr = ( SysDescr(), Uptime() )  # sorted by object name

def cbFun(tspDsp, transportDomain, transportAddress, wholeMsg):
    while wholeMsg:
        reqVer = api.decodeMessageVersion(wholeMsg)
        pMod = api.protoModules[reqVer]        
        reqMsg, wholeMsg = decoder.decode(
            wholeMsg, asn1Spec=pMod.Message(),
            )
        print 'Message version %s from %s:%s: ' % (
            reqVer, transportDomain, transportAddress
            )
        print reqMsg.prettyPrinter()
        rspMsg = pMod.apiMessage.getResponse(reqMsg)
        rspPDU = pMod.apiMessage.getPDU(rspMsg)        
        reqPDU = pMod.apiMessage.getPDU(reqMsg)        
        # Support only a single PDU type (but any proto version)
        if reqPDU.isSameTypeWith(pMod.GetNextRequestPDU()):
            # Produce response var-binds
            varBinds = []; errorIndex = -1
            for oid, val in pMod.apiPDU.getVarBinds(reqPDU):
                print transportAddress, oid, val
                errorIndex = errorIndex + 1
                # Search next OID to report
                nextIdx = bisect.bisect(mibInstr, oid)
                if nextIdx == len(mibInstr):
                    # Out of MIB
                    pMod.apiPDU.setEndOfMIBIndices(rspPDU, errorIndex)
                else:
                    # Report value if OID is found
                    varBinds.append(
                        (mibInstr[nextIdx].name, mibInstr[nextIdx](reqVer))
                        )
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
