"""Command Generator Application (GET)"""
from pysnmp.proto.rfc3412 import MsgAndPduDispatcher
from pysnmp.proto.api import alpha

# PDU version to use
versionId = alpha.protoVersionId1
ver = alpha.protoVersions[versionId]

msgAndPduDsp = MsgAndPduDispatcher()

# UDP is default transport, initialize client mode
msgAndPduDsp.transportDispatcher.getTransport('udp').openClientMode()

# Configure target SNMP agent at LCD
( snmpCommunityEntry, )  \
  =  msgAndPduDsp.mibInstrumController.mibBuilder.importSymbols(
    'SNMP-COMMUNITY-MIB', 'snmpCommunityEntry'
    )
msgAndPduDsp.mibInstrumController.writeVars(
    (snmpCommunityEntry.getInstNameByIndex(2, 'myAgentIdx'), 'public'),
    (snmpCommunityEntry.getInstNameByIndex(3, 'myAgentIdx'), 'myAgent')
    )

pdu = ver.TrapPdu()

# Traps have quite different semantics among proto versions
if pdu.apiAlphaGetProtoVersionId() == alpha.protoVersionId1:
    pdu.apiAlphaSetEnterprise((1,3,6,1,1,2,3,4,1))
    pdu.apiAlphaSetGenericTrap('coldStart')

msgAndPduDsp.sendPdu(
    transportDomain='udp', transportAddress=('127.0.0.1', 1162),
    messageProcessingModel=versionId,
    pduVersion=versionId,
    securityName='myAgent',
    PDU=pdu
    )
msgAndPduDsp.transportDispatcher.runDispatcher(liveForever=0)
