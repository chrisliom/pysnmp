# PySNMP SMI module. Autogenerated from smidump -f python SNMP-NOTIFICATION-MIB
# by libsmi2pysnmp-0.0.2 at Tue Nov  2 18:55:42 2004,
# Python version (2, 2, 1, 'final', 0)

# Imported just in case new ASN.1 types would be created
from pysnmp.asn1 import subtypes

# Imports

( Integer, ObjectIdentifier, OctetString, ) = mibBuilder.importSymbols("ASN1", "Integer", "ObjectIdentifier", "OctetString")
( SnmpAdminString, ) = mibBuilder.importSymbols("SNMP-FRAMEWORK-MIB", "SnmpAdminString")
( SnmpTagValue, snmpTargetBasicGroup, snmpTargetBasicGroup, snmpTargetBasicGroup, snmpTargetParamsMPModel, snmpTargetParamsName, snmpTargetParamsRowStatus, snmpTargetParamsSecurityLevel, snmpTargetParamsSecurityModel, snmpTargetParamsSecurityName, snmpTargetParamsStorageType, snmpTargetResponseGroup, ) = mibBuilder.importSymbols("SNMP-TARGET-MIB", "SnmpTagValue", "snmpTargetBasicGroup", "snmpTargetBasicGroup", "snmpTargetBasicGroup", "snmpTargetParamsMPModel", "snmpTargetParamsName", "snmpTargetParamsRowStatus", "snmpTargetParamsSecurityLevel", "snmpTargetParamsSecurityModel", "snmpTargetParamsSecurityName", "snmpTargetParamsStorageType", "snmpTargetResponseGroup")
( ModuleCompliance, ObjectGroup, ) = mibBuilder.importSymbols("SNMPv2-CONF", "ModuleCompliance", "ObjectGroup")
( Bits, Integer32, ModuleIdentity, MibIdentifier, MibVariable, MibTable, MibTableRow, MibTableColumn, TimeTicks, snmpModules, ) = mibBuilder.importSymbols("SNMPv2-SMI", "Bits", "Integer32", "ModuleIdentity", "MibIdentifier", "MibVariable", "MibTable", "MibTableRow", "MibTableColumn", "TimeTicks", "snmpModules")
( RowStatus, StorageType, ) = mibBuilder.importSymbols("SNMPv2-TC", "RowStatus", "StorageType")

# Objects

snmpNotificationMIB = ModuleIdentity((1, 3, 6, 1, 6, 3, 13))
snmpNotifyObjects = MibIdentifier((1, 3, 6, 1, 6, 3, 13, 1))
snmpNotifyTable = MibTable((1, 3, 6, 1, 6, 3, 13, 1, 1))
snmpNotifyEntry = MibTableRow((1, 3, 6, 1, 6, 3, 13, 1, 1, 1)).setIndexNames((1, "SNMP-NOTIFICATION-MIB", "snmpNotifyName"))
snmpNotifyName = MibTableColumn((1, 3, 6, 1, 6, 3, 13, 1, 1, 1, 1)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueRangeConstraint(1, 32))).setMaxAccess("noaccess"))
snmpNotifyTag = MibTableColumn((1, 3, 6, 1, 6, 3, 13, 1, 1, 1, 2)).setColumnInitializer(MibVariable((), SnmpTagValue()).setMaxAccess("readcreate"))
snmpNotifyType = MibTableColumn((1, 3, 6, 1, 6, 3, 13, 1, 1, 1, 3)).setColumnInitializer(MibVariable((), Integer().addConstraints(subtypes.SingleValueConstraint(2,1,)).addNamedValues(("trap", 1), ("inform", 2), ).set(1)).setMaxAccess("readcreate"))
snmpNotifyStorageType = MibTableColumn((1, 3, 6, 1, 6, 3, 13, 1, 1, 1, 4)).setColumnInitializer(MibVariable((), StorageType()).setMaxAccess("readcreate"))
snmpNotifyRowStatus = MibTableColumn((1, 3, 6, 1, 6, 3, 13, 1, 1, 1, 5)).setColumnInitializer(MibVariable((), RowStatus()).setMaxAccess("readcreate"))
snmpNotifyFilterProfileTable = MibTable((1, 3, 6, 1, 6, 3, 13, 1, 2))
snmpNotifyFilterProfileEntry = MibTableRow((1, 3, 6, 1, 6, 3, 13, 1, 2, 1)).setIndexNames((1, "SNMP-TARGET-MIB", "snmpTargetParamsName"))
snmpNotifyFilterProfileName = MibTableColumn((1, 3, 6, 1, 6, 3, 13, 1, 2, 1, 1)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueRangeConstraint(1, 32))).setMaxAccess("readcreate"))
snmpNotifyFilterProfileStorType = MibTableColumn((1, 3, 6, 1, 6, 3, 13, 1, 2, 1, 2)).setColumnInitializer(MibVariable((), StorageType()).setMaxAccess("readcreate"))
snmpNotifyFilterProfileRowStatus = MibTableColumn((1, 3, 6, 1, 6, 3, 13, 1, 2, 1, 3)).setColumnInitializer(MibVariable((), RowStatus()).setMaxAccess("readcreate"))
snmpNotifyFilterTable = MibTable((1, 3, 6, 1, 6, 3, 13, 1, 3))
snmpNotifyFilterEntry = MibTableRow((1, 3, 6, 1, 6, 3, 13, 1, 3, 1)).setIndexNames((0, "SNMP-NOTIFICATION-MIB", "snmpNotifyFilterProfileName"), (0, "SNMP-NOTIFICATION-MIB", "snmpNotifyFilterSubtree"))
snmpNotifyFilterSubtree = MibTableColumn((1, 3, 6, 1, 6, 3, 13, 1, 3, 1, 1)).setColumnInitializer(MibVariable((), ObjectIdentifier()).setMaxAccess("noaccess"))
snmpNotifyFilterMask = MibTableColumn((1, 3, 6, 1, 6, 3, 13, 1, 3, 1, 2)).setColumnInitializer(MibVariable((), OctetString().addConstraints(subtypes.ValueRangeConstraint(0, 16)).set('')).setMaxAccess("readcreate"))
snmpNotifyFilterType = MibTableColumn((1, 3, 6, 1, 6, 3, 13, 1, 3, 1, 3)).setColumnInitializer(MibVariable((), Integer().addConstraints(subtypes.SingleValueConstraint(1,2,)).addNamedValues(("included", 1), ("excluded", 2), ).set(1)).setMaxAccess("readcreate"))
snmpNotifyFilterStorageType = MibTableColumn((1, 3, 6, 1, 6, 3, 13, 1, 3, 1, 4)).setColumnInitializer(MibVariable((), StorageType()).setMaxAccess("readcreate"))
snmpNotifyFilterRowStatus = MibTableColumn((1, 3, 6, 1, 6, 3, 13, 1, 3, 1, 5)).setColumnInitializer(MibVariable((), RowStatus()).setMaxAccess("readcreate"))
snmpNotifyConformance = MibIdentifier((1, 3, 6, 1, 6, 3, 13, 3))
snmpNotifyCompliances = MibIdentifier((1, 3, 6, 1, 6, 3, 13, 3, 1))
snmpNotifyGroups = MibIdentifier((1, 3, 6, 1, 6, 3, 13, 3, 2))

# Augmentions

# Groups

snmpNotifyFilterGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 13, 3, 2, 2)).setObjects(("SNMP-NOTIFICATION-MIB", "snmpNotifyFilterRowStatus"), ("SNMP-NOTIFICATION-MIB", "snmpNotifyFilterProfileStorType"), ("SNMP-NOTIFICATION-MIB", "snmpNotifyFilterStorageType"), ("SNMP-NOTIFICATION-MIB", "snmpNotifyFilterProfileName"), ("SNMP-NOTIFICATION-MIB", "snmpNotifyFilterMask"), ("SNMP-NOTIFICATION-MIB", "snmpNotifyFilterType"), ("SNMP-NOTIFICATION-MIB", "snmpNotifyFilterProfileRowStatus"), )
snmpNotifyGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 13, 3, 2, 1)).setObjects(("SNMP-NOTIFICATION-MIB", "snmpNotifyTag"), ("SNMP-NOTIFICATION-MIB", "snmpNotifyRowStatus"), ("SNMP-NOTIFICATION-MIB", "snmpNotifyStorageType"), ("SNMP-NOTIFICATION-MIB", "snmpNotifyType"), )

# Exports

# Objects
mibBuilder.exportSymbols("SNMP-NOTIFICATION-MIB", snmpNotificationMIB=snmpNotificationMIB, snmpNotifyObjects=snmpNotifyObjects, snmpNotifyTable=snmpNotifyTable, snmpNotifyEntry=snmpNotifyEntry, snmpNotifyName=snmpNotifyName, snmpNotifyTag=snmpNotifyTag, snmpNotifyType=snmpNotifyType, snmpNotifyStorageType=snmpNotifyStorageType, snmpNotifyRowStatus=snmpNotifyRowStatus, snmpNotifyFilterProfileTable=snmpNotifyFilterProfileTable, snmpNotifyFilterProfileEntry=snmpNotifyFilterProfileEntry, snmpNotifyFilterProfileName=snmpNotifyFilterProfileName, snmpNotifyFilterProfileStorType=snmpNotifyFilterProfileStorType, snmpNotifyFilterProfileRowStatus=snmpNotifyFilterProfileRowStatus, snmpNotifyFilterTable=snmpNotifyFilterTable, snmpNotifyFilterEntry=snmpNotifyFilterEntry, snmpNotifyFilterSubtree=snmpNotifyFilterSubtree, snmpNotifyFilterMask=snmpNotifyFilterMask, snmpNotifyFilterType=snmpNotifyFilterType, snmpNotifyFilterStorageType=snmpNotifyFilterStorageType, snmpNotifyFilterRowStatus=snmpNotifyFilterRowStatus, snmpNotifyConformance=snmpNotifyConformance, snmpNotifyCompliances=snmpNotifyCompliances, snmpNotifyGroups=snmpNotifyGroups)

# Groups
mibBuilder.exportSymbols("SNMP-NOTIFICATION-MIB", snmpNotifyFilterGroup=snmpNotifyFilterGroup, snmpNotifyGroup=snmpNotifyGroup)
