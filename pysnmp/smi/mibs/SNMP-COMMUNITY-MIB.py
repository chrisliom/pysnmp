# PySNMP SMI module. Autogenerated from smidump -f python SNMP-COMMUNITY-MIB
# by libsmi2pysnmp-0.0.2 at Tue Nov  2 18:49:04 2004,
# Python version (2, 2, 1, 'final', 0)

# Imported just in case new ASN.1 types would be created
from pysnmp.asn1 import subtypes

# Imports

( Integer, ObjectIdentifier, OctetString, ) = mibBuilder.importSymbols("ASN1", "Integer", "ObjectIdentifier", "OctetString")
( SnmpAdminString, SnmpEngineID, ) = mibBuilder.importSymbols("SNMP-FRAMEWORK-MIB", "SnmpAdminString", "SnmpEngineID")
( SnmpTagValue, snmpTargetAddrEntry, ) = mibBuilder.importSymbols("SNMP-TARGET-MIB", "SnmpTagValue", "snmpTargetAddrEntry")
( ModuleCompliance, ObjectGroup, ) = mibBuilder.importSymbols("SNMPv2-CONF", "ModuleCompliance", "ObjectGroup")
( Bits, Integer32, Integer32, IpAddress, ModuleIdentity, MibIdentifier, MibVariable, MibTable, MibTableRow, MibTableColumn, TimeTicks, snmpModules, ) = mibBuilder.importSymbols("SNMPv2-SMI", "Bits", "Integer32", "Integer32", "IpAddress", "ModuleIdentity", "MibIdentifier", "MibVariable", "MibTable", "MibTableRow", "MibTableColumn", "TimeTicks", "snmpModules")
( RowStatus, StorageType, ) = mibBuilder.importSymbols("SNMPv2-TC", "RowStatus", "StorageType")

# Objects

snmpCommunityMIB = ModuleIdentity((1, 3, 6, 1, 6, 3, 18))
snmpCommunityMIBObjects = MibIdentifier((1, 3, 6, 1, 6, 3, 18, 1))
snmpCommunityTable = MibTable((1, 3, 6, 1, 6, 3, 18, 1, 1))
snmpCommunityEntry = MibTableRow((1, 3, 6, 1, 6, 3, 18, 1, 1, 1)).setIndexNames((1, "SNMP-COMMUNITY-MIB", "snmpCommunityIndex"))
snmpCommunityIndex = MibTableColumn((1, 3, 6, 1, 6, 3, 18, 1, 1, 1, 1)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueRangeConstraint(1, 32))).setMaxAccess("noaccess"))
snmpCommunityName = MibTableColumn((1, 3, 6, 1, 6, 3, 18, 1, 1, 1, 2)).setColumnInitializer(MibVariable((), OctetString()).setMaxAccess("readcreate"))
snmpCommunitySecurityName = MibTableColumn((1, 3, 6, 1, 6, 3, 18, 1, 1, 1, 3)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueRangeConstraint(1, 32))).setMaxAccess("readcreate"))
snmpCommunityContextEngineID = MibTableColumn((1, 3, 6, 1, 6, 3, 18, 1, 1, 1, 4)).setColumnInitializer(MibVariable((), SnmpEngineID()).setMaxAccess("readcreate"))
snmpCommunityContextName = MibTableColumn((1, 3, 6, 1, 6, 3, 18, 1, 1, 1, 5)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueRangeConstraint(0, 32)).set('')).setMaxAccess("readcreate"))
snmpCommunityTransportTag = MibTableColumn((1, 3, 6, 1, 6, 3, 18, 1, 1, 1, 6)).setColumnInitializer(MibVariable((), SnmpTagValue()).setMaxAccess("readcreate"))
snmpCommunityStorageType = MibTableColumn((1, 3, 6, 1, 6, 3, 18, 1, 1, 1, 7)).setColumnInitializer(MibVariable((), StorageType()).setMaxAccess("readcreate"))
snmpCommunityStatus = MibTableColumn((1, 3, 6, 1, 6, 3, 18, 1, 1, 1, 8)).setColumnInitializer(MibVariable((), RowStatus()).setMaxAccess("readcreate"))
snmpTargetAddrExtTable = MibTable((1, 3, 6, 1, 6, 3, 18, 1, 2))
snmpTargetAddrExtEntry = MibTableRow((1, 3, 6, 1, 6, 3, 18, 1, 2, 1))
snmpTargetAddrTMask = MibTableColumn((1, 3, 6, 1, 6, 3, 18, 1, 2, 1, 1)).setColumnInitializer(MibVariable((), OctetString().addConstraints(subtypes.ValueRangeConstraint(0, 255)).set('')).setMaxAccess("readcreate"))
snmpTargetAddrMMS = MibTableColumn((1, 3, 6, 1, 6, 3, 18, 1, 2, 1, 2)).setColumnInitializer(MibVariable((), Integer32().addConstraints(subtypes.ValueRangeConstraint(484, 2147483647)).set(484)).setMaxAccess("readcreate"))
snmpTrapAddress = MibVariable((1, 3, 6, 1, 6, 3, 18, 1, 3), IpAddress()).setMaxAccess("notifyonly")
snmpTrapCommunity = MibVariable((1, 3, 6, 1, 6, 3, 18, 1, 4), OctetString()).setMaxAccess("notifyonly")
snmpCommunityMIBConformance = MibIdentifier((1, 3, 6, 1, 6, 3, 18, 2))
snmpCommunityMIBCompliances = MibIdentifier((1, 3, 6, 1, 6, 3, 18, 2, 1))
snmpCommunityMIBGroups = MibIdentifier((1, 3, 6, 1, 6, 3, 18, 2, 2))

# Augmentions
snmpTargetAddrEntry, = mibBuilder.importSymbols("SNMP-TARGET-MIB", "snmpTargetAddrEntry")
snmpTargetAddrEntry.registerAugmentions(("SNMP-COMMUNITY-MIB", "snmpTargetAddrExtEntry"))

# Groups

snmpProxyTrapForwardGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 18, 2, 2, 3)).setObjects(("SNMP-COMMUNITY-MIB", "snmpTrapAddress"), ("SNMP-COMMUNITY-MIB", "snmpTrapCommunity"), )
snmpCommunityGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 18, 2, 2, 1)).setObjects(("SNMP-COMMUNITY-MIB", "snmpCommunitySecurityName"), ("SNMP-COMMUNITY-MIB", "snmpCommunityStorageType"), ("SNMP-COMMUNITY-MIB", "snmpCommunityContextName"), ("SNMP-COMMUNITY-MIB", "snmpTargetAddrMMS"), ("SNMP-COMMUNITY-MIB", "snmpTargetAddrTMask"), ("SNMP-COMMUNITY-MIB", "snmpCommunityName"), ("SNMP-COMMUNITY-MIB", "snmpCommunityContextEngineID"), ("SNMP-COMMUNITY-MIB", "snmpCommunityStatus"), ("SNMP-COMMUNITY-MIB", "snmpCommunityTransportTag"), )

# Exports

# Objects
mibBuilder.exportSymbols("SNMP-COMMUNITY-MIB", snmpCommunityMIB=snmpCommunityMIB, snmpCommunityMIBObjects=snmpCommunityMIBObjects, snmpCommunityTable=snmpCommunityTable, snmpCommunityEntry=snmpCommunityEntry, snmpCommunityIndex=snmpCommunityIndex, snmpCommunityName=snmpCommunityName, snmpCommunitySecurityName=snmpCommunitySecurityName, snmpCommunityContextEngineID=snmpCommunityContextEngineID, snmpCommunityContextName=snmpCommunityContextName, snmpCommunityTransportTag=snmpCommunityTransportTag, snmpCommunityStorageType=snmpCommunityStorageType, snmpCommunityStatus=snmpCommunityStatus, snmpTargetAddrExtTable=snmpTargetAddrExtTable, snmpTargetAddrExtEntry=snmpTargetAddrExtEntry, snmpTargetAddrTMask=snmpTargetAddrTMask, snmpTargetAddrMMS=snmpTargetAddrMMS, snmpTrapAddress=snmpTrapAddress, snmpTrapCommunity=snmpTrapCommunity, snmpCommunityMIBConformance=snmpCommunityMIBConformance, snmpCommunityMIBCompliances=snmpCommunityMIBCompliances, snmpCommunityMIBGroups=snmpCommunityMIBGroups)

# Groups
mibBuilder.exportSymbols("SNMP-COMMUNITY-MIB", snmpProxyTrapForwardGroup=snmpProxyTrapForwardGroup, snmpCommunityGroup=snmpCommunityGroup)
