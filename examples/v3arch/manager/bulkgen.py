from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdgen, error
from pysnmp.carrier.asynsock.dgram import udp

snmpEngine = engine.SnmpEngine()

# v1/2 setup
# addV1System(snmpEngine, 'public')

# v3 setup
config.addV3User(snmpEngine, 'test-user', 'authkey1', 'md5', 'privkey1', 'des')

# Transport params
config.addTargetParams(snmpEngine, 'myParams', 'test-user', 'authPriv')

# Transport addresses
config.addTargetAddr(
    snmpEngine, 'myRouter', config.snmpUDPDomain,
    ('127.0.0.1', 161), 'myParams'    
    )

# Transport
config.addSocketTransport(
    snmpEngine,
    config.snmpUDPDomain,
    udp.UdpSocketTransport().openClientMode()
    )

def cbFun(sendRequesthandle, errorIndication, errorStatus, errorIndex,
          varBindTable, cbCtx):
    if errorIndication or errorStatus:
        raise error.ApplicationReturn(
            errorIndication=errorIndication,
            errorStatus=errorStatus
            )
    for varBindRow in varBindTable:
        for oid, val in varBindRow:
            print '%s = %s' % (oid, val)    

cmdgen.BulkCmdGen().sendReq(
    snmpEngine, 'myRouter', 0, 25, (((1,3,6,1,2,1,1), None),), cbFun
    )

try:
    snmpEngine.transportDispatcher.runDispatcher()
except error.ApplicationReturn, applicationReturn:
    print applicationReturn