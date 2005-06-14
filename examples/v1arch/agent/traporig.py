"""Notification Originator Application (TRAP)"""
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram.udp import UdpSocketTransport
from pyasn1.codec.ber import encoder
from pysnmp.proto import api

# Protocol version to use
verID = api.protoVersion1
pMod = api.protoModules[verID]

# Build PDU
trapPDU =  pMod.TrapPDU()
pMod.apiTrapPDU.setDefaults(trapPDU)

# Traps have quite different semantics among proto versions
if verID == api.protoVersion1:
    pMod.apiTrapPDU.setEnterprise(trapPDU, (1,3,6,1,1,2,3,4,1))
    pMod.apiTrapPDU.setGenericTrap(trapPDU, 'coldStart')

# Build message
trapMsg = pMod.Message()
pMod.apiMessage.setDefaults(trapMsg)
pMod.apiMessage.setCommunity(trapMsg, 'public')
pMod.apiMessage.setPDU(trapMsg, trapPDU)

dsp = AsynsockDispatcher(udp=UdpSocketTransport().openClientMode())
dsp.sendMessage(encoder.encode(trapMsg), 'udp', ('localhost', 1162)) # 162
dsp.runDispatcher(liveForever=0)
dsp.closeDispatcher()
