"""Notification Originator Application"""
from pysnmp import setApiVersion
setApiVersion('v4')
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram.udp import UdpSocketTransport
from pysnmp.proto.api import alpha

# Protocol version to use
ver = alpha.protoVersions[alpha.protoVersionId1]

req = ver.Message()
req.apiAlphaSetCommunity('public')
req.apiAlphaSetPdu(ver.TrapPdu())

# Traps have quite different semantics among proto versions
if req.apiAlphaGetProtoVersionId() == alpha.protoVersionId1:
    req.apiAlphaGetPdu().apiAlphaSetEnterprise((1,3,6,1,1,2,3,4,1))
    req.apiAlphaGetPdu().apiAlphaSetGenericTrap('coldStart')

dsp = AsynsockDispatcher(udp=UdpSocketTransport().openClientMode())
dsp.sendMessage(req.berEncode(), 'udp', ('localhost', 1162)) # 162
dsp.runDispatcher(liveForever=0)
dsp.closeDispatcher()
