from pysnmp.asn1 import subtypes

OctetString, = mibBuilder.importSymbols(
    'ASN1', 'OctetString'
    )
ModuleIdentity, ObjectIdentity, MibIdentifier, \
                MibVariable, MibTable, MibTableRow, MibTableColumn, \
                snmpModules, Counter32 = mibBuilder.importSymbols(
    'SNMPv2-SMI', 'ModuleIdentity', 'ObjectIdentity', 'MibIdentifier',
    'MibVariable', 'MibTable', 'MibTableRow', 'MibTableColumn',
    'snmpModules', 'Counter32'
    )
TextualConvention, TestAndIncr, RowStatus, RowPointer, StorageType, \
                   AutonomousType = mibBuilder.importSymbols(
    'SNMPv2-TC', 'TextualConvention', 'TestAndIncr', 'RowStatus',
    'RowPointer', 'StorageType', 'AutonomousType'
    )
SnmpAdminString, SnmpEngineID, snmpAuthProtocols, \
                 snmpPrivProtocols = mibBuilder.importSymbols(
    'SNMP-FRAMEWORK-MIB', 'SnmpAdminString', 'SnmpEngineID',
    'snmpAuthProtocols', 'snmpPrivProtocols'
    )

snmpUsmMIB = ModuleIdentity(snmpModules.name + (15,))

usmMIBObjects = MibIdentifier(snmpUsmMIB.name + (1,))
usmMIBConformance = MibIdentifier(snmpUsmMIB.name + (2,))

# OI's
usmNoAuthProtocol = ObjectIdentity(snmpAuthProtocols.name + (1,))
usmHMACMD5AuthProtocol = ObjectIdentity(snmpAuthProtocols.name + (2,))
usmHMACSHAAuthProtocol = ObjectIdentity(snmpAuthProtocols.name + (3,))
usmNoPrivProtocol = ObjectIdentity(snmpPrivProtocols.name + (1,))
usmDESPrivProtocol = ObjectIdentity(snmpPrivProtocols.name + (2,))

# TC's
class KeyChange(TextualConvention, OctetString): pass

# MIB Objects

usmStats = MibIdentifier(usmMIBObjects.name + (1,))

usmStatsUnsupportedSecLevels = MibVariable(usmStats.name + (1,), Counter32()).setMaxAccess('readonly')

usmStatsNotInTimeWindows = MibVariable(usmStats.name + (2,), Counter32()).setMaxAccess('readonly')

usmStatsUnknownUserNames = MibVariable(usmStats.name + (3,), Counter32()).setMaxAccess('readonly')

usmStatsUnknownEngineIDs = MibVariable(usmStats.name + (4,), Counter32()).setMaxAccess('readonly')

usmStatsWrongDigests = MibVariable(usmStats.name + (5,), Counter32()).setMaxAccess('readonly')

usmStatsDecryptionErrors = MibVariable(usmStats.name + (6,), Counter32()).setMaxAccess('readonly')

usmUser = MibIdentifier(usmMIBObjects.name + (2,))

usmUserSpinLock = MibVariable(usmUser.name + (1,), TestAndIncr()).setMaxAccess('readwrite')

# usmUserTable

usmUserTable = MibTable(usmUser.name + (2,))

usmUserEntry = MibTableRow(usmUserTable.name + (1,))

usmUserEngineID = MibTableColumn(usmUserEntry.name + (1,)).setColumnInitializer(MibVariable((), SnmpEngineID()).setMaxAccess('noaccess'))

usmUserName = MibTableColumn(usmUserEntry.name + (2,)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueRangeConstraint(1, 32))).setMaxAccess('noaccess'))

usmUserSecurityName = MibTableColumn(usmUserEntry.name + (3,)).setColumnInitializer(MibVariable((), SnmpAdminString()).setMaxAccess('readonly'))

usmUserCloneFrom = MibTableColumn(usmUserEntry.name + (4,)).setColumnInitializer(MibVariable((), RowPointer()).setMaxAccess('readcreate'))

usmUserAuthProtocol = MibTableColumn(usmUserEntry.name + (5,)).setColumnInitializer(MibVariable((), AutonomousType(usmNoAuthProtocol.name)).setMaxAccess('readcreate'))

usmUserAuthKeyChange = MibTableColumn(usmUserEntry.name + (6,)).setColumnInitializer(MibVariable((), KeyChange('')).setMaxAccess('readcreate'))

usmUserOwnAuthKeyChange = MibTableColumn(usmUserEntry.name + (7,)).setColumnInitializer(MibVariable((), KeyChange('')).setMaxAccess('readcreate'))

usmUserPrivProtocol = MibTableColumn(usmUserEntry.name + (8,)).setColumnInitializer(MibVariable((), AutonomousType(usmNoPrivProtocol.name)).setMaxAccess('readcreate'))

usmUserPrivKeyChange = MibTableColumn(usmUserEntry.name + (9,)).setColumnInitializer(MibVariable((), KeyChange('')).setMaxAccess('readcreate'))

usmUserOwnPrivKeyChange = MibTableColumn(usmUserEntry.name + (10,)).setColumnInitializer(MibVariable((), KeyChange('')).setMaxAccess('readcreate'))

usmUserPublic = MibTableColumn(usmUserEntry.name + (11,)).setColumnInitializer(MibVariable((), OctetString().addConstraints(subtypes.ValueRangeConstraint(0, 32))).setMaxAccess('readcreate'))

usmUserStorageType = MibTableColumn(usmUserEntry.name + (12,)).setColumnInitializer(MibVariable((),StorageType (3)).setMaxAccess('readcreate'))

usmUserStatus = MibTableColumn(usmUserEntry.name + (13,)).setColumnInitializer(MibVariable((), RowStatus()).setMaxAccess('readcreate'))

# Set table indices
usmUserEntry.setIndexNames(
    (0, modName, 'usmUserEngineID'), (0, modName, 'usmUserName')
    )

mibBuilder.exportSymbols(
    modName,
    snmpUsmMIB=snmpUsmMIB,
    usmMIBObjects=usmMIBObjects,
    usmMIBConformance=usmMIBConformance,
    usmNoAuthProtocol=usmNoAuthProtocol,
    usmHMACMD5AuthProtocol=usmHMACMD5AuthProtocol,
    usmNoPrivProtocol=usmNoPrivProtocol,
    usmDESPrivProtocol=usmDESPrivProtocol,
    KeyChange=KeyChange,
    usmStats=usmStats,
    usmStatsUnsupportedSecLevels=usmStatsUnsupportedSecLevels,
    usmStatsNotInTimeWindows=usmStatsNotInTimeWindows,
    usmStatsUnknownUserNames=usmStatsUnknownUserNames,
    usmStatsUnknownEngineIDs=usmStatsUnknownEngineIDs,
    usmStatsWrongDigests=usmStatsWrongDigests,
    usmStatsDecryptionErrors=usmStatsDecryptionErrors,
    usmUser=usmUser,
    usmUserSpinLock=usmUserSpinLock,
    usmUserTable=usmUserTable,
    usmUserEntry=usmUserEntry,
    usmUserEngineID=usmUserEngineID,
    usmUserName=usmUserName,
    usmUserSecurityName=usmUserSecurityName,
    usmUserCloneFrom=usmUserCloneFrom,
    usmUserAuthProtocol=usmUserAuthProtocol,
    usmUserAuthKeyChange=usmUserAuthKeyChange,
    usmUserPrivProtocol=usmUserPrivProtocol,
    usmUserPrivKeyChange=usmUserPrivKeyChange,
    usmUserOwnPrivKeyChange=usmUserOwnPrivKeyChange,
    usmUserPublic=usmUserPublic,
    usmUserStorageType=usmUserStorageType,
    usmUserStatus=usmUserStatus
    )
