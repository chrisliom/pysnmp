from pysnmp.asn1 import subtypes

OctetString, Integer,ObjectIdentifier = mibBuilder.importSymbols(
    'ASN1', 'OctetString', 'Integer', 'ObjectIdentifier'
    )
ModuleIdentity, MibIdentifier, MibVariable, MibTable, MibTableRow, \
                MibTableColumn, snmpModules = mibBuilder.importSymbols(
    'SNMPv2-SMI', 'ModuleIdentity', 'MibIdentifier', 'MibVariable',
    'MibTable', 'MibTableRow', 'MibTableColumn', 'snmpModules'
    )
TestAndIncr, RowStatus, StorageType = mibBuilder.importSymbols(
    'SNMPv2-TC', 'TestAndIncr', 'RowStatus', 'StorageType'
    )
SnmpAdminString, SnmpSecurityLevel, \
                 SnmpSecurityModel = mibBuilder.importSymbols(
    'SNMP-FRAMEWORK-MIB', 'SnmpAdminString', 'SnmpSecurityLevel',
    'SnmpSecurityModel'
    )

snmpVacmMIB = ModuleIdentity(snmpModules.name + (16,))

vacmMIBObjects = MibIdentifier(snmpVacmMIB.name + (1,))
vacmMIBConformance = MibIdentifier(snmpVacmMIB.name + (2,))

# vacmContextTable

vacmContextTable = MibTable(vacmMIBObjects.name + (1,))
vacmContextEntry = MibTableRow(vacmContextTable.name + (1,))
vacmContextName = MibTableColumn(vacmContextEntry.name + (1,)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueRangeConstraint(0, 32))).setMaxAccess('readonly'))

# vacmSecurityToGroupTable

vacmSecurityToGroupTable = MibTable(vacmMIBObjects.name + (2,))
vacmSecurityToGroupEntry = MibTableRow(vacmSecurityToGroupTable.name + (1,)).setIndexNames((0, modName, 'vacmSecurityModel'), (0, modName, 'vacmSecurityName'))

vacmSecurityModel = MibTableColumn(vacmSecurityToGroupEntry.name + (1,)).setColumnInitializer(MibVariable((), SnmpSecurityModel().addConstraints(subtypes.ValueRangeConstraint(1,2147483647))).setMaxAccess('noaccess'))

vacmSecurityName = MibTableColumn(vacmSecurityToGroupEntry.name + (2,)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueRangeConstraint(1, 32))).setMaxAccess('noaccess'))

vacmGroupName = MibTableColumn(vacmSecurityToGroupEntry.name + (3,)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueRangeConstraint(1, 32))).setMaxAccess('readcreate'))

vacmSecurityToGroupStorageType = MibTableColumn(vacmSecurityToGroupEntry.name + (4,)).setColumnInitializer(MibVariable((), StorageType()).setMaxAccess('readcreate'))

vacmSecurityToGroupStatus = MibTableColumn(vacmSecurityToGroupEntry.name + (5,)).setColumnInitializer(MibVariable((), RowStatus()).setMaxAccess('noaccess'))

# vacmAccessTable

vacmAccessTable = MibTable(vacmMIBObjects.name + (4,))

vacmAccessEntry = MibTableRow(vacmAccessTable.name + (1,)).setIndexNames(
    (0, modName, 'vacmGroupName'),
    (0, modName, 'vacmAccessContextPrefix'),
    (0, modName, 'vacmAccessSecurityModel'),
    (0, modName, 'vacmAccessSecurityLevel')
    )
vacmSecurityToGroupEntry.registerAugmentions((modName, 'vacmAccessEntry'))

vacmAccessContextPrefix = MibTableColumn(vacmAccessEntry.name + (1,)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueRangeConstraint(0, 32))).setMaxAccess('noaccess'))

vacmAccessSecurityModel = MibTableColumn(vacmAccessEntry.name + (2,)).setColumnInitializer(MibVariable((), SnmpSecurityModel()).setMaxAccess('noaccess'))

vacmAccessSecurityLevel = MibTableColumn(vacmAccessEntry.name + (3,)).setColumnInitializer(MibVariable((), SnmpSecurityLevel()).setMaxAccess('noaccess'))

vacmAccessContextMatch = MibTableColumn(vacmAccessEntry.name + (4,)).setColumnInitializer(MibVariable((), Integer(1).addConstraints(subtypes.SingleValueConstraint(1, 2))).setMaxAccess('readcreate'))

vacmAccessReadViewName = MibTableColumn(vacmAccessEntry.name + (5,)).setColumnInitializer(MibVariable((), SnmpAdminString("").addConstraints(subtypes.ValueRangeConstraint(0, 32))).setMaxAccess('readcreate'))

vacmAccessWriteViewName = MibTableColumn(vacmAccessEntry.name + (6,)).setColumnInitializer(MibVariable((), SnmpAdminString("").addConstraints(subtypes.ValueRangeConstraint(0, 32))).setMaxAccess('readcreate'))

vacmAccessNotifyViewName = MibTableColumn(vacmAccessEntry.name + (7,)).setColumnInitializer(MibVariable((), SnmpAdminString("").addConstraints(subtypes.ValueRangeConstraint(0, 32))).setMaxAccess('readcreate'))

vacmAccessStorageType = MibTableColumn(vacmAccessEntry.name + (8,)).setColumnInitializer(MibVariable((), StorageType(3)).setMaxAccess('readcreate'))

vacmAccessStatus = MibTableColumn(vacmAccessEntry.name + (9,)).setColumnInitializer(MibVariable((), RowStatus()).setMaxAccess('readcreate'))

vacmMIBViews = MibIdentifier(vacmMIBObjects.name + (5,))

vacmViewSpinLock = MibVariable(vacmMIBViews.name + (1,), TestAndIncr()).setMaxAccess('readwrite')

# vacmViewTreeFamilyTable

vacmViewTreeFamilyTable = MibTable(vacmMIBViews.name + (2,))

vacmViewTreeFamilyEntry = MibTableRow(vacmViewTreeFamilyTable.name + (1,))
vacmViewTreeFamilyEntry.setIndexNames(
    (0, modName, 'vacmViewTreeFamilyViewName'),
    (0, modName, 'vacmViewTreeFamilySubtree')
    )

vacmViewTreeFamilyViewName = MibTableColumn(vacmViewTreeFamilyEntry.name + (1,)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueRangeConstraint(1, 32))).setMaxAccess('noaccess'))

vacmViewTreeFamilySubtree = MibTableColumn(vacmViewTreeFamilyEntry.name + (2,)).setColumnInitializer(MibVariable((), ObjectIdentifier()).setMaxAccess('noaccess'))

vacmViewTreeFamilyMask = MibTableColumn(vacmViewTreeFamilyEntry.name + (3,)).setColumnInitializer(MibVariable((), OctetString('').addConstraints(subtypes.ValueRangeConstraint(0, 16))).setMaxAccess('readcreate'))

vacmViewTreeFamilyType = MibTableColumn(vacmViewTreeFamilyEntry.name + (4,)).setColumnInitializer(MibVariable((), Integer(1).addConstraints(subtypes.SingleValueConstraint(1, 2))).setMaxAccess('readcreate'))

vacmViewTreeFamilyStorageType = MibTableColumn(vacmViewTreeFamilyEntry.name + (5,)).setColumnInitializer(MibVariable((), StorageType()).setMaxAccess('readcreate'))

vacmViewTreeFamilyStatus = MibTableColumn(vacmViewTreeFamilyEntry.name + (6,)).setColumnInitializer(MibVariable((), RowStatus()).setMaxAccess('readcreate'))

mibBuilder.exportSymbols(
    modName,
    snmpVacmMIB=snmpVacmMIB,
    vacmMIBObjects=vacmMIBObjects,
    vacmMIBConformance=vacmMIBConformance,
    vacmContextTable=vacmContextTable,
    vacmContextEntry=vacmContextEntry,
    vacmContextName=vacmContextName,
    vacmSecurityToGroupTable=vacmSecurityToGroupTable,
    vacmSecurityToGroupEntry=vacmSecurityToGroupEntry,
    vacmSecurityModel=vacmSecurityModel,
    vacmSecurityName=vacmSecurityName,
    vacmGroupName=vacmGroupName,
    vacmSecurityToGroupStorageType=vacmSecurityToGroupStorageType,
    vacmSecurityToGroupStatus=vacmSecurityToGroupStatus,
    vacmAccessTable=vacmAccessTable,
    vacmAccessEntry=vacmAccessEntry,
    vacmAccessContextPrefix=vacmAccessContextPrefix,
    vacmAccessSecurityModel=vacmAccessSecurityModel,
    vacmAccessSecurityLevel=vacmAccessSecurityLevel,
    vacmAccessContextMatch=vacmAccessContextMatch,
    vacmAccessReadViewName=vacmAccessReadViewName,
    vacmAccessWriteViewName=vacmAccessWriteViewName,
    vacmAccessNotifyViewName=vacmAccessNotifyViewName,
    vacmAccessStorageType=vacmAccessStorageType,
    vacmAccessStatus=vacmAccessStatus,
    vacmMIBViews=vacmMIBViews,
    vacmViewSpinLock=vacmViewSpinLock,
    vacmViewTreeFamilyTable=vacmViewTreeFamilyTable,
    vacmViewTreeFamilyEntry=vacmViewTreeFamilyEntry,
    vacmViewTreeFamilyViewName=vacmViewTreeFamilyViewName,
    vacmViewTreeFamilySubtree=vacmViewTreeFamilySubtree,
    vacmViewTreeFamilyMask=vacmViewTreeFamilyMask,
    vacmViewTreeFamilyType=vacmViewTreeFamilyType,
    vacmViewTreeFamilyStorageType=vacmViewTreeFamilyStorageType,
    vacmViewTreeFamilyStatus=vacmViewTreeFamilyStatus
    )
    
