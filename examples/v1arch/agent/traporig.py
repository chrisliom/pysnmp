"""Notification Originator Application"""
from pysnmp import setApiVersion
setApiVersion('v4')
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram.udp import UdpSocketTransport
from pysnmp.proto import omni

# Protocol version to use
ver = omni.protoVersions[omni.protoVersionId1]

req = ver.Message()
req.omniSetCommunity('public')
req.omniSetPdu(ver.TrapPdu())

# Traps have quite different semantics among proto versions
if req.omniGetProtoVersionId() == omni.protoVersionId1:
    req.omniGetPdu().omniSetEnterprise((1,3,6,1,1,2,3,4,1))
    req.omniGetPdu().omniSetGenericTrap('coldStart')

dsp = AsynsockDispatcher(udp=UdpSocketTransport().openClientMode())
dsp.sendMessage(req.berEncode(), 'udp', ('localhost', 1162)) # 162
dsp.runDispatcher(liveForever=0)
dsp.closeDispatcher()
