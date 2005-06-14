"""Notification Originator Application (TRAP)"""
from pysnmp.proto.rfc3412 import MsgAndPduDispatcher
from pysnmp.proto import api

# Protocol version to use
protoVersionID = api.protoVersion1
pMod = api.protoModules[protoVersionID]

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

pdu = pMod.TrapPDU()
pMod.apiTrapPDU.setDefaults(pdu)  # XXX

# Traps have quite different semantics among proto versions
if protoVersionID == api.protoVersion1:
    pMod.apiTrapPDU.setEnterprise(pdu, (1,3,6,1,1,2,3,4,1))
    pMod.apiTrapPDU.setGenericTrap(pdu, 'coldStart')

msgAndPduDsp.sendPdu(
    transportDomain='udp', transportAddress=('127.0.0.1', 1162),
    messageProcessingModel=protoVersionID,
    pduVersion=protoVersionID,
    securityName='myAgent',
    PDU=pdu
    )
msgAndPduDsp.transportDispatcher.runDispatcher(liveForever=0)
