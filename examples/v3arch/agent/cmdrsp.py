"""Command Responder Application (GET PDU)"""
from pysnmp.entity import engine, config
from pysnmp.carrier.asynsock.dgram import udp
from pysnmp.entity.rfc3413 import cmdrsp, context

# Create SNMP engine with autogenernated engineID and pre-bound
# to socket transport dispatcher
snmpEngine = engine.SnmpEngine()

# Setup transport endpoint
config.addSocketTransport(
    snmpEngine,
    udp.domainName,
    udp.UdpSocketTransport().openServerMode(('127.0.0.1', 1161))
    )

# Create and put on-line my managed object
MibVariable, = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder.importSymbols('SNMPv2-SMI', 'MibVariable')
OctetString, = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder.importSymbols('ASN1', 'OctetString')
myMibVariable = MibVariable(
    (1,3,6,1,4,1,20408,2,1), OctetString('hello, NMS!')
    ).setMaxAccess("readwrite")
snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder.exportSymbols('PYSNMP-EXAMPLE-MIB', myMibVariable=myMibVariable)  # creating MIB

# v1/2 setup
config.addV1System(snmpEngine, 'test-agent', 'public')

# v3 setup
config.addV3User(
    snmpEngine, 'test-user',
    config.usmHMACMD5AuthProtocol, 'authkey1',
    config.usmDESPrivProtocol, 'privkey1'
    )
    
# VACM setup
config.addContext(snmpEngine, '')
config.addRwUser(snmpEngine, 1, 'test-agent', 'noAuthNoPriv', (1,3,6)) # v1
config.addRwUser(snmpEngine, 2, 'test-agent', 'noAuthNoPriv', (1,3,6)) # v2c
config.addRwUser(snmpEngine, 3, 'test-user', 'authPriv', (1,3,6)) # v3

# SNMP context
snmpContext = context.SnmpContext(snmpEngine)

# Apps registration
cmdrsp.GetCommandResponder(snmpEngine, snmpContext)
cmdrsp.SetCommandResponder(snmpEngine, snmpContext)
cmdrsp.NextCommandResponder(snmpEngine, snmpContext)
cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)
snmpEngine.transportDispatcher.jobStarted(1) # this job would never finish
snmpEngine.transportDispatcher.runDispatcher()
