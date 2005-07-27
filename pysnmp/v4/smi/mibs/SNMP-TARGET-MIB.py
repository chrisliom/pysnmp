# PySNMP SMI module. Autogenerated from smidump -f python SNMP-TARGET-MIB
# by libsmi2pysnmp-0.0.3-alpha at Tue Apr 26 17:41:24 2005,
# Python version (2, 4, 0, 'final', 0)

# Imported just in case new ASN.1 types would be created
from pyasn1.type import constraint, namedval

# Imports

( Integer, ObjectIdentifier, OctetString, ) = mibBuilder.importSymbols("ASN1", "Integer", "ObjectIdentifier", "OctetString")
( SnmpAdminString, SnmpMessageProcessingModel, SnmpSecurityLevel, SnmpSecurityModel, ) = mibBuilder.importSymbols("SNMP-FRAMEWORK-MIB", "SnmpAdminString", "SnmpMessageProcessingModel", "SnmpSecurityLevel", "SnmpSecurityModel")
( ModuleCompliance, ObjectGroup, ) = mibBuilder.importSymbols("SNMPv2-CONF", "ModuleCompliance", "ObjectGroup")
( Bits, Counter32, Integer32, Integer32, ModuleIdentity, MibIdentifier, MibVariable, MibTable, MibTableRow, MibTableColumn, TimeTicks, snmpModules, ) = mibBuilder.importSymbols("SNMPv2-SMI", "Bits", "Counter32", "Integer32", "Integer32", "ModuleIdentity", "MibIdentifier", "MibVariable", "MibTable", "MibTableRow", "MibTableColumn", "TimeTicks", "snmpModules")
( RowStatus, StorageType, TAddress, TDomain, TextualConvention, TestAndIncr, TimeInterval, ) = mibBuilder.importSymbols("SNMPv2-TC", "RowStatus", "StorageType", "TAddress", "TDomain", "TextualConvention", "TestAndIncr", "TimeInterval")

# Types

class SnmpTagList(OctetString, TextualConvention):
    subtypeSpec = OctetString.subtypeSpec+constraint.ValueSizeConstraint(0,255)
    pass

class SnmpTagValue(OctetString, TextualConvention):
    subtypeSpec = OctetString.subtypeSpec+constraint.ValueSizeConstraint(0,255)
    pass


# Objects

snmpTargetMIB = ModuleIdentity((1, 3, 6, 1, 6, 3, 12))
snmpTargetObjects = MibIdentifier((1, 3, 6, 1, 6, 3, 12, 1))
snmpTargetSpinLock = MibVariable((1, 3, 6, 1, 6, 3, 12, 1, 1), TestAndIncr()).setMaxAccess("readwrite")
snmpTargetAddrTable = MibTable((1, 3, 6, 1, 6, 3, 12, 1, 2))
snmpTargetAddrEntry = MibTableRow((1, 3, 6, 1, 6, 3, 12, 1, 2, 1)).setIndexNames((1, "SNMP-TARGET-MIB", "snmpTargetAddrName"))
snmpTargetAddrName = MibTableColumn((1, 3, 6, 1, 6, 3, 12, 1, 2, 1, 1)).setColumnInitializer(MibVariable((), SnmpAdminString().subtype(subtypeSpec=constraint.ValueSizeConstraint(1, 32))).setMaxAccess("noaccess"))
snmpTargetAddrTDomain = MibTableColumn((1, 3, 6, 1, 6, 3, 12, 1, 2, 1, 2)).setColumnInitializer(MibVariable((), TDomain()).setMaxAccess("readcreate"))
snmpTargetAddrTAddress = MibTableColumn((1, 3, 6, 1, 6, 3, 12, 1, 2, 1, 3)).setColumnInitializer(MibVariable((), TAddress()).setMaxAccess("readcreate"))
snmpTargetAddrTimeout = MibTableColumn((1, 3, 6, 1, 6, 3, 12, 1, 2, 1, 4)).setColumnInitializer(MibVariable((), TimeInterval(1500)).setMaxAccess("readcreate"))
snmpTargetAddrRetryCount = MibTableColumn((1, 3, 6, 1, 6, 3, 12, 1, 2, 1, 5)).setColumnInitializer(MibVariable((), Integer32(3).subtype(subtypeSpec=constraint.ValueRangeConstraint(0, 255)).subtype(3)).setMaxAccess("readcreate"))
snmpTargetAddrTagList = MibTableColumn((1, 3, 6, 1, 6, 3, 12, 1, 2, 1, 6)).setColumnInitializer(MibVariable((), SnmpTagList()).setMaxAccess("readcreate"))
snmpTargetAddrParams = MibTableColumn((1, 3, 6, 1, 6, 3, 12, 1, 2, 1, 7)).setColumnInitializer(MibVariable((), SnmpAdminString().subtype(subtypeSpec=constraint.ValueSizeConstraint(1, 32))).setMaxAccess("readcreate"))
snmpTargetAddrStorageType = MibTableColumn((1, 3, 6, 1, 6, 3, 12, 1, 2, 1, 8)).setColumnInitializer(MibVariable((), StorageType()).setMaxAccess("readcreate"))
snmpTargetAddrRowStatus = MibTableColumn((1, 3, 6, 1, 6, 3, 12, 1, 2, 1, 9)).setColumnInitializer(MibVariable((), RowStatus()).setMaxAccess("readcreate"))
snmpTargetParamsTable = MibTable((1, 3, 6, 1, 6, 3, 12, 1, 3))
snmpTargetParamsEntry = MibTableRow((1, 3, 6, 1, 6, 3, 12, 1, 3, 1)).setIndexNames((1, "SNMP-TARGET-MIB", "snmpTargetParamsName"))
snmpTargetParamsName = MibTableColumn((1, 3, 6, 1, 6, 3, 12, 1, 3, 1, 1)).setColumnInitializer(MibVariable((), SnmpAdminString().subtype(subtypeSpec=constraint.ValueSizeConstraint(1, 32))).setMaxAccess("noaccess"))
snmpTargetParamsMPModel = MibTableColumn((1, 3, 6, 1, 6, 3, 12, 1, 3, 1, 2)).setColumnInitializer(MibVariable((), SnmpMessageProcessingModel()).setMaxAccess("readcreate"))
snmpTargetParamsSecurityModel = MibTableColumn((1, 3, 6, 1, 6, 3, 12, 1, 3, 1, 3)).setColumnInitializer(MibVariable((), SnmpSecurityModel().subtype(subtypeSpec=constraint.ValueRangeConstraint(1, 2147483647L))).setMaxAccess("readcreate"))
snmpTargetParamsSecurityName = MibTableColumn((1, 3, 6, 1, 6, 3, 12, 1, 3, 1, 4)).setColumnInitializer(MibVariable((), SnmpAdminString()).setMaxAccess("readcreate"))
snmpTargetParamsSecurityLevel = MibTableColumn((1, 3, 6, 1, 6, 3, 12, 1, 3, 1, 5)).setColumnInitializer(MibVariable((), SnmpSecurityLevel()).setMaxAccess("readcreate"))
snmpTargetParamsStorageType = MibTableColumn((1, 3, 6, 1, 6, 3, 12, 1, 3, 1, 6)).setColumnInitializer(MibVariable((), StorageType()).setMaxAccess("readcreate"))
snmpTargetParamsRowStatus = MibTableColumn((1, 3, 6, 1, 6, 3, 12, 1, 3, 1, 7)).setColumnInitializer(MibVariable((), RowStatus()).setMaxAccess("readcreate"))
snmpUnavailableContexts = MibVariable((1, 3, 6, 1, 6, 3, 12, 1, 4), Counter32()).setMaxAccess("readonly")
snmpUnknownContexts = MibVariable((1, 3, 6, 1, 6, 3, 12, 1, 5), Counter32()).setMaxAccess("readonly")
snmpTargetConformance = MibIdentifier((1, 3, 6, 1, 6, 3, 12, 3))
snmpTargetCompliances = MibIdentifier((1, 3, 6, 1, 6, 3, 12, 3, 1))
snmpTargetGroups = MibIdentifier((1, 3, 6, 1, 6, 3, 12, 3, 2))

# Augmentions

# Groups

snmpTargetResponseGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 12, 3, 2, 2)).setObjects(("SNMP-TARGET-MIB", "snmpTargetAddrRetryCount"), ("SNMP-TARGET-MIB", "snmpTargetAddrTimeout"), )
snmpTargetCommandResponderGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 12, 3, 2, 3)).setObjects(("SNMP-TARGET-MIB", "snmpUnavailableContexts"), ("SNMP-TARGET-MIB", "snmpUnknownContexts"), )
snmpTargetBasicGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 12, 3, 2, 1)).setObjects(("SNMP-TARGET-MIB", "snmpTargetAddrTDomain"), ("SNMP-TARGET-MIB", "snmpTargetAddrParams"), ("SNMP-TARGET-MIB", "snmpTargetParamsRowStatus"), ("SNMP-TARGET-MIB", "snmpTargetParamsMPModel"), ("SNMP-TARGET-MIB", "snmpTargetAddrStorageType"), ("SNMP-TARGET-MIB", "snmpTargetParamsSecurityName"), ("SNMP-TARGET-MIB", "snmpTargetAddrRowStatus"), ("SNMP-TARGET-MIB", "snmpTargetAddrTAddress"), ("SNMP-TARGET-MIB", "snmpTargetParamsStorageType"), ("SNMP-TARGET-MIB", "snmpTargetAddrTagList"), ("SNMP-TARGET-MIB", "snmpTargetSpinLock"), ("SNMP-TARGET-MIB", "snmpTargetParamsSecurityLevel"), ("SNMP-TARGET-MIB", "snmpTargetParamsSecurityModel"), )

# Exports

# Types
mibBuilder.exportSymbols("SNMP-TARGET-MIB", SnmpTagList=SnmpTagList, SnmpTagValue=SnmpTagValue)

# Objects
mibBuilder.exportSymbols("SNMP-TARGET-MIB", snmpTargetMIB=snmpTargetMIB, snmpTargetObjects=snmpTargetObjects, snmpTargetSpinLock=snmpTargetSpinLock, snmpTargetAddrTable=snmpTargetAddrTable, snmpTargetAddrEntry=snmpTargetAddrEntry, snmpTargetAddrName=snmpTargetAddrName, snmpTargetAddrTDomain=snmpTargetAddrTDomain, snmpTargetAddrTAddress=snmpTargetAddrTAddress, snmpTargetAddrTimeout=snmpTargetAddrTimeout, snmpTargetAddrRetryCount=snmpTargetAddrRetryCount, snmpTargetAddrTagList=snmpTargetAddrTagList, snmpTargetAddrParams=snmpTargetAddrParams, snmpTargetAddrStorageType=snmpTargetAddrStorageType, snmpTargetAddrRowStatus=snmpTargetAddrRowStatus, snmpTargetParamsTable=snmpTargetParamsTable, snmpTargetParamsEntry=snmpTargetParamsEntry, snmpTargetParamsName=snmpTargetParamsName, snmpTargetParamsMPModel=snmpTargetParamsMPModel, snmpTargetParamsSecurityModel=snmpTargetParamsSecurityModel, snmpTargetParamsSecurityName=snmpTargetParamsSecurityName, snmpTargetParamsSecurityLevel=snmpTargetParamsSecurityLevel, snmpTargetParamsStorageType=snmpTargetParamsStorageType, snmpTargetParamsRowStatus=snmpTargetParamsRowStatus, snmpUnavailableContexts=snmpUnavailableContexts, snmpUnknownContexts=snmpUnknownContexts, snmpTargetConformance=snmpTargetConformance, snmpTargetCompliances=snmpTargetCompliances, snmpTargetGroups=snmpTargetGroups)

# Groups
mibBuilder.exportSymbols("SNMP-TARGET-MIB", snmpTargetResponseGroup=snmpTargetResponseGroup, snmpTargetCommandResponderGroup=snmpTargetCommandResponderGroup, snmpTargetBasicGroup=snmpTargetBasicGroup)
