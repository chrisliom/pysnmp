ModuleIdentity, ObjectIdentity, MibIdentifier, \
                MibVariable, snmpModules, Counter32 = mibBuilder.importSymbols(
    'SNMPv2-SMI', 'ModuleIdentity', 'ObjectIdentity', 'MibIdentifier',
    'MibVariable', 'snmpModules', 'Counter32'
    )

snmpMPDMIB = ModuleIdentity(snmpModules.name + (11,))

snmpMPDAdmin = MibIdentifier(snmpMPDMIB.name + (1,))
snmpMPDMIBObjects = MibIdentifier(snmpMPDMIB.name + (2,))
snmpMPDMIBConformance = MibIdentifier(snmpMPDMIB.name + (3,))

snmpMPDStats = MibIdentifier(snmpMPDMIBObjects.name + (1,))

snmpUnknownSecurityModels = MibVariable(snmpMPDStats.name + (1,), Counter32()).setMaxAccess('readonly')

snmpInvalidMsgs = MibVariable(snmpMPDStats.name + (2,), Counter32()).setMaxAccess('readonly')

snmpUnknownPDUHandlers = MibVariable(snmpMPDStats.name + (3,), Counter32()).setMaxAccess('readonly')

mibBuilder.exportSymbols(
    modName,
    snmpMPDMIB=snmpMPDMIB,
    snmpMPDAdmin=snmpMPDAdmin,
    snmpMPDMIBObjects=snmpMPDMIBObjects,
    snmpMPDMIBConformance=snmpMPDMIBConformance,
    snmpMPDStats=snmpMPDStats,
    snmpUnknownSecurityModels=snmpUnknownSecurityModels,
    snmpInvalidMsgs=snmpInvalidMsgs,
    snmpUnknownPDUHandlers=snmpUnknownPDUHandlers
    )
