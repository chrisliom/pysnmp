( MibScalarInstance, ) = mibBuilder.importSymbols(
    'SNMPv2-SMI',
    'MibScalarInstance'
    )

( snmpTargetSpinLock,
  snmpUnavailableContexts,
  snmpUnknownContexts ) = mibBuilder.importSymbols(
    'SNMP-TARGET-MIB',
    'snmpTargetSpinLock',
    'snmpUnavailableContexts',
    'snmpUnknownContexts'
    )
    
__snmpTargetSpinLock = MibScalarInstance(snmpTargetSpinLock.name, (0,), snmpTargetSpinLock.syntax)
__snmpUnavailableContexts = MibScalarInstance(snmpUnavailableContexts.name, (0,), snmpUnavailableContexts.syntax)
__snmpUnknownContexts = MibScalarInstance(snmpUnknownContexts.name, (0,), snmpUnknownContexts.syntax)

mibBuilder.exportSymbols(
        '__SNMP-TARGET-MIB',
        snmpTargetSpinLock = __snmpTargetSpinLock,
        snmpUnavailableContexts = __snmpUnavailableContexts,
        snmpUnknownContexts = __snmpUnknownContexts
        )
        
