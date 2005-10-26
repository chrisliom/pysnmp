( MibScalarInstance, ) = mibBuilder.importSymbols(
    'SNMPv2-SMI',
    'MibScalarInstance'
    )
( snmpUnknownSecurityModels,
  snmpInvalidMsgs,
  snmpUnknownPDUHandlers ) = mibBuilder.importSymbols(
    'SNMP-MPD-MIB',
    'snmpUnknownSecurityModels',
    'snmpInvalidMsgs',
    'snmpUnknownPDUHandlers',
    )

__snmpUnknownSecurityModels = MibScalarInstance(snmpUnknownSecurityModels.name, (0,), snmpUnknownSecurityModels.syntax)
__snmpInvalidMsgs = MibScalarInstance(snmpInvalidMsgs.name, (0,), snmpInvalidMsgs.syntax)
__snmpUnknownPDUHandlers = MibScalarInstance(snmpUnknownPDUHandlers.name, (0,), snmpUnknownPDUHandlers.syntax)

mibBuilder.exportSymbols(
    '__SNMP-MPD-MIB',
    snmpUnknownSecurityModels = __snmpUnknownSecurityModels,
    snmpInvalidMsgs = __snmpInvalidMsgs,
    snmpUnknownPDUHandlers = __snmpUnknownPDUHandlers
    )
