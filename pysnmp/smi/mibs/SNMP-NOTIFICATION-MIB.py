from pysnmp.asn1 import subtypes

OctetString, Integer, ObjectIdentifier = mibBuilder.importSymbols(
    'ASN1', 'OctetString', 'Integer', 'ObjectIdentifier'
    )
ModuleIdentity, ObjectIdentity, MibIdentifier, \
           MibVariable, MibTable, MibTableRow, MibTableColumn, \
           snmpModules = mibBuilder.importSymbols(
    'SNMPv2-SMI', 'ModuleIdentity', 'ObjectIdentity',
    'MibIdentifier', 'MibVariable', 'MibTable', 'MibTableRow',
    'MibTableColumn', 'snmpModules'
    )
RowStatus, StorageType = mibBuilder.importSymbols(
    'SNMPv2-TC', 'RowStatus', 'StorageType'
    )
SnmpAdminString, = mibBuilder.importSymbols(
    'SNMP-FRAMEWORK-MIB', 'SnmpAdminString'
    )
SnmpTagValue, snmpTargetParamsName = mibBuilder.importSymbols(
    'SNMP-TARGET-MIB', 'SnmpTagValue', 'snmpTargetParamsName'
    )

snmpNotificationMIB = ModuleIdentity(snmpModules.name + (13,))

snmpNotifyObjects = MibIdentifier(snmpNotificationMIB.name + (1,))
snmpNotifyConformance = MibIdentifier(snmpNotificationMIB.name + (3,))

# snmpNotifyTable

snmpNotifyTable = MibTable(snmpNotifyObjects.name + (1,))
snmpNotifyEntry = MibTableRow(snmpNotifyTable.name + (1,)).setIndexNames((1, modName, 'snmpNotifyName'))

snmpNotifyName = MibTableColumn(snmpNotifyEntry.name + (1,)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueRangeConstraint(1, 32))).setMaxAccess('noaccess'))

snmpNotifyTag = MibTableColumn(snmpNotifyEntry.name + (2,)).setColumnInitializer(MibVariable((), SnmpTagValue("")).setMaxAccess('readcreate'))

snmpNotifyType = MibTableColumn(snmpNotifyEntry.name + (3,)).setColumnInitializer(MibVariable((), Integer(1).addConstraints(subtypes.SingleValueConstraint(1, 2))).setMaxAccess('readcreate'))

snmpNotifyStorageType = MibTableColumn(snmpNotifyEntry.name + (4,)).setColumnInitializer(MibVariable((), StorageType(3)).setMaxAccess('readcreate'))

snmpNotifyRowStatus = MibTableColumn(snmpNotifyEntry.name + (5,)).setColumnInitializer(MibVariable((), RowStatus()).setMaxAccess('readcreate'))

# snmpNotifyFilterProfileTable

snmpNotifyFilterProfileTable = MibTable(snmpNotifyObjects.name + (2,))

snmpNotifyFilterProfileEntry = MibTableRow(snmpNotifyFilterProfileTable.name + (1,)).setIndexNames((1, 'SNMP-TARGET-MIB', 'snmpTargetParamsName'))
snmpTargetParamsEntry, = mibBuilder.importSymbols('SNMP-TARGET-MIB', 'snmpTargetParamsEntry')
snmpTargetParamsEntry.registerAugmentions((modName, 'snmpNotifyFilterProfileEntry'))
snmpNotifyFilterProfileName = MibTableColumn(snmpNotifyFilterProfileEntry.name + (1,)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueRangeConstraint(1, 32))).setMaxAccess('readcreate'))

snmpNotifyFilterProfileStorType = MibTableColumn(snmpNotifyFilterProfileEntry.name + (2,)).setColumnInitializer(MibVariable((), StorageType(3)).setMaxAccess('readcreate'))

snmpNotifyFilterProfileRowStatus = MibTableColumn(snmpNotifyFilterProfileEntry.name + (3,)).setColumnInitializer(MibVariable((), RowStatus()).setMaxAccess('readcreate'))

# snmpNotifyFilterTable

snmpNotifyFilterTable = MibTable(snmpNotifyObjects.name + (3,))

snmpNotifyFilterEntry = MibTableRow(snmpNotifyFilterTable.name + (1,)).setIndexNames((0, modName, 'snmpNotifyFilterProfileName'), (1, modName, 'snmpNotifyFilterSubtree'))

snmpNotifyFilterProfileEntry.registerAugmentions((modName, 'snmpNotifyFilterEntry'))

snmpNotifyFilterSubtree = MibTableColumn(snmpNotifyFilterEntry.name + (1,)).setColumnInitializer(MibVariable((), ObjectIdentifier()).setMaxAccess('noaccess'))

snmpNotifyFilterMask = MibTableColumn(snmpNotifyFilterEntry.name + (2,)).setColumnInitializer(MibVariable((), OctetString("").addConstraints(subtypes.ValueSizeConstraint(0, 16))).setMaxAccess('readcreate'))

snmpNotifyFilterType = MibTableColumn(snmpNotifyFilterEntry.name + (3,)).setColumnInitializer(MibVariable((), Integer(1).addConstraints(subtypes.SingleValueConstraint(1, 2))).setMaxAccess('readcreate'))

snmpNotifyFilterStorageType = MibTableColumn(snmpNotifyFilterEntry.name + (4,)).setColumnInitializer(MibVariable((), StorageType(3)).setMaxAccess('readcreate'))

snmpNotifyFilterRowStatus = MibTableColumn(snmpNotifyFilterEntry.name + (5,)).setColumnInitializer(MibVariable((), RowStatus()).setMaxAccess('readcreate'))

mibBuilder.exportSymbols(
    modName,
    snmpNotificationMIB=snmpNotificationMIB,
    snmpNotifyObjects=snmpNotifyObjects,
    snmpNotifyConformance=snmpNotifyConformance,
    snmpNotifyTable=snmpNotifyTable,
    snmpNotifyEntry=snmpNotifyEntry,
    snmpNotifyName=snmpNotifyName,
    snmpNotifyTag=snmpNotifyTag,
    snmpNotifyType=snmpNotifyType,
    snmpNotifyStorageType=snmpNotifyStorageType,
    snmpNotifyFilterProfileTable=snmpNotifyFilterProfileTable,
    snmpNotifyFilterProfileEntry=snmpNotifyFilterProfileEntry,
    snmpNotifyFilterProfileName=snmpNotifyFilterProfileName,
    snmpNotifyFilterProfileStorType=snmpNotifyFilterProfileStorType,
    snmpNotifyFilterProfileRowStatus=snmpNotifyFilterProfileRowStatus,
    snmpNotifyFilterTable=snmpNotifyFilterTable,
    snmpNotifyFilterEntry=snmpNotifyFilterEntry,
    snmpNotifyFilterSubtree=snmpNotifyFilterSubtree,
    snmpNotifyFilterMask=snmpNotifyFilterMask,
    snmpNotifyFilterType=snmpNotifyFilterType,
    snmpNotifyFilterStorageType=snmpNotifyFilterStorageType,
    snmpNotifyFilterRowStatus=snmpNotifyFilterRowStatus
    )
