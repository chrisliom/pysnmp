from pysnmp.asn1 import subtypes

OctetString, = mibBuilder.importSymbols(
    'ASN1', 'OctetString'
    )
IpAddress, ModuleIdentity, ObjectIdentity, MibIdentifier, \
           MibVariable, MibTable, MibTableRow, MibTableColumn, \
           Integer32, snmpModules = mibBuilder.importSymbols(
    'SNMPv2-SMI', 'IpAddress', 'ModuleIdentity', 'ObjectIdentity',
    'MibIdentifier', 'MibVariable', 'MibTable', 'MibTableRow',
    'MibTableColumn', 'Integer32', 'snmpModules'
    )
RowStatus, StorageType = mibBuilder.importSymbols(
    'SNMPv2-TC', 'RowStatus', 'StorageType'
    )
SnmpAdminString, SnmpEngineID = mibBuilder.importSymbols(
    'SNMP-FRAMEWORK-MIB', 'SnmpAdminString', 'SnmpEngineID'
    )
SnmpTagValue, snmpTargetAddrEntry = mibBuilder.importSymbols(
    'SNMP-TARGET-MIB', 'SnmpTagValue', 'snmpTargetAddrEntry'
    )

snmpCommunityMIB = ModuleIdentity(snmpModules.name + (18,))

snmpCommunityMIBObjects = MibIdentifier(snmpCommunityMIB.name + (1,))
snmpCommunityMIBConformance = MibIdentifier(snmpCommunityMIB.name + (2,))

# snmpCommunityTable

snmpCommunityTable = MibTable(snmpCommunityMIBObjects.name + (1,))

snmpCommunityEntry = MibTableRow(snmpCommunityTable.name + (1,))

snmpCommunityIndex = MibTableColumn(snmpCommunityEntry.name + (1,)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueSizeConstraint(1, 32))).setMaxAccess('noaccess'))

snmpCommunityName = MibTableColumn(snmpCommunityEntry.name + (2,)).setColumnInitializer(MibVariable((), OctetString('public')).setMaxAccess('readcreate'))

snmpCommunitySecurityName = MibTableColumn(snmpCommunityEntry.name + (3,)).setColumnInitializer(MibVariable((), SnmpAdminString('public').addConstraints(subtypes.ValueSizeConstraint(1, 32))).setMaxAccess('readcreate'))

snmpCommunityContextEngineID = MibTableColumn(snmpCommunityEntry.name + (4,)).setColumnInitializer(MibVariable((), SnmpEngineID()).setMaxAccess('readcreate'))

snmpCommunityContextName = MibTableColumn(snmpCommunityEntry.name + (5,)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueSizeConstraint(0, 32))).setMaxAccess('readcreate'))

snmpCommunityTransportTag = MibTableColumn(snmpCommunityEntry.name + (6,)).setColumnInitializer(MibVariable((), SnmpTagValue('')).setMaxAccess('readcreate'))

snmpCommunityStorageType = MibTableColumn(snmpCommunityEntry.name + (7,)).setColumnInitializer(MibVariable((), StorageType()).setMaxAccess('readcreate'))

snmpCommunityStatus = MibTableColumn(snmpCommunityEntry.name + (8,)).setColumnInitializer(MibVariable((), RowStatus()).setMaxAccess('readcreate'))

snmpCommunityEntry.setIndexNames((1, modName, 'snmpCommunityIndex'))

# snmpTargetAddrExtTable

snmpTargetAddrExtTable = MibTable(snmpCommunityMIBObjects.name + (2,))

snmpTargetAddrExtEntry = MibTableRow(snmpTargetAddrExtTable.name + (1,))

snmpTargetAddrTMask = MibTableColumn(snmpTargetAddrExtEntry.name + (1,)).setColumnInitializer(MibVariable((), OctetString().addConstraints(subtypes.ValueSizeConstraint(0, 255))).setMaxAccess('readcreate'))

snmpTargetAddrMMS = MibTableColumn(snmpTargetAddrExtEntry.name + (2,)).setColumnInitializer(MibVariable((), Integer32().addConstraints(subtypes.ValueRangeConstraint(484, 2147483647))).setMaxAccess('readcreate'))

snmpTargetAddrExtEntry.setIndexNames((0, 'SNMP-TARGET-MIB', 'snmpTargetAddrName'))
snmpTargetAddrEntry.registerAugmentions((modName, 'snmpTargetAddrExtEntry'))

snmpTrapAddress = MibVariable(snmpCommunityMIBObjects.name + (3,), IpAddress()).setMaxAccess('notifyonly')

snmpTrapCommunity = MibVariable(snmpCommunityMIBObjects.name + (4,), OctetString()).setMaxAccess('notifyonly')

mibBuilder.exportSymbols(
    modName,
    snmpCommunityMIB=snmpCommunityMIB,
    snmpCommunityMIBObjects=snmpCommunityMIBObjects,
    snmpCommunityMIBConformance=snmpCommunityMIBConformance,
    snmpCommunityTable=snmpCommunityTable,
    snmpCommunityEntry=snmpCommunityEntry,
    snmpCommunityIndex=snmpCommunityIndex,
    snmpCommunityName=snmpCommunityName,
    snmpCommunitySecurityName=snmpCommunitySecurityName,
    snmpCommunityContextEngineID=snmpCommunityContextEngineID,
    snmpCommunityContextName=snmpCommunityContextName,
    snmpCommunityTransportTag=snmpCommunityTransportTag,
    snmpCommunityStorageType=snmpCommunityStorageType,
    snmpCommunityStatus=snmpCommunityStatus,
    snmpTargetAddrExtTable=snmpTargetAddrExtTable,
    snmpTargetAddrExtEntry=snmpTargetAddrExtEntry,
    snmpTargetAddrTMask=snmpTargetAddrTMask,
    snmpTargetAddrMMS=snmpTargetAddrMMS,
    snmpTrapAddress=snmpTrapAddress,
    snmpTrapCommunity=snmpTrapCommunity
    )
