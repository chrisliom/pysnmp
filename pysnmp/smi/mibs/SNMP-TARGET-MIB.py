from pysnmp.asn1 import subtypes

OctetString, Integer = mibBuilder.importSymbols(
    'ASN1', 'OctetString', 'Integer'
    )
ModuleIdentity, MibIdentifier, MibVariable, MibTable, \
                MibTableRow, MibTableColumn, snmpModules, Counter32, \
                Integer32 = mibBuilder.importSymbols(
    'SNMPv2-SMI', 'ModuleIdentity', 'MibIdentifier',
    'MibVariable', 'MibTable', 'MibTableRow', 'MibTableColumn',
    'snmpModules', 'Counter32', 'Integer32'
    )
TextualConvention, TDomain, TAddress, TimeInterval, RowStatus, \
                   StorageType, TestAndIncr = mibBuilder.importSymbols(
    'SNMPv2-TC', 'TextualConvention', 'TDomain', 'TAddress', 'TimeInterval',
    'RowStatus', 'StorageType', 'TestAndIncr'
    )    
SnmpSecurityModel, SnmpMessageProcessingModel, SnmpSecurityLevel, \
                   SnmpAdminString = mibBuilder.importSymbols(
    'SNMP-FRAMEWORK-MIB', 'SnmpSecurityModel', 'SnmpMessageProcessingModel',
    'SnmpSecurityLevel', 'SnmpAdminString'
    )

snmpTargetMIB = ModuleIdentity(snmpModules.name + (12,))

snmpTargetObjects = MibIdentifier(snmpTargetMIB.name + (1,))
snmpTargetConformance = MibIdentifier(snmpTargetMIB.name + (3,))

# TC's

class SnmpTagValue(TextualConvention, OctetString):
    subtypeConstraints = OctetString.subtypeConstraints + (
        subtypes.ValueSizeConstraint(0, 255),
        )
    displayHint = "255t"
    
class SnmpTagList(TextualConvention, OctetString):
    subtypeConstraints = OctetString.subtypeConstraints + (
        subtypes.ValueSizeConstraint(0, 255),
        )
    displayHint = "255t"

# MIB objects

snmpTargetSpinLock = MibVariable(
    snmpTargetObjects.name + (1,), TestAndIncr()
    ).setMaxAccess('readwrite')

# snmpTargetAddrTable

snmpTargetAddrTable = MibTable(snmpTargetObjects.name + (2,))

snmpTargetAddrEntry = MibTableRow(snmpTargetAddrTable.name + (1,)).setIndexNames((1, modName, 'snmpTargetAddrTable'))

snmpTargetAddrName = MibTableColumn(snmpTargetAddrEntry.name + (1,)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueRangeConstraint(1, 32))).setMaxAccess('noaccess'))

snmpTargetAddrTDomain = MibTableColumn(snmpTargetAddrEntry.name + (2,)).setColumnInitializer(MibVariable((), TDomain()).setMaxAccess('readcreate'))

snmpTargetAddrTAddress = MibTableColumn(snmpTargetAddrEntry.name + (3,)).setColumnInitializer(MibVariable((), TAddress()).setMaxAccess('readcreate'))

snmpTargetAddrTimeout = MibTableColumn(snmpTargetAddrEntry.name + (4,)).setColumnInitializer(MibVariable((), TimeInterval(1500)).setMaxAccess('readcreate'))

snmpTargetAddrRetryCount = MibTableColumn(snmpTargetAddrEntry.name + (5,)).setColumnInitializer(MibVariable((), Integer32(3).addConstraints(subtypes.ValueRangeConstraint(0, 255))).setMaxAccess('readcreate'))

snmpTargetAddrTagList = MibTableColumn(snmpTargetAddrEntry.name + (6,)).setColumnInitializer(MibVariable((), SnmpTagList("")).setMaxAccess('readcreate'))

snmpTargetAddrParams = MibTableColumn(snmpTargetAddrEntry.name + (7,)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueSizeConstraint(1, 32))).setMaxAccess('readcreate'))

snmpTargetAddrStorageType = MibTableColumn(snmpTargetAddrEntry.name + (8,)).setColumnInitializer(MibVariable((), StorageType(3)).setMaxAccess('readcreate'))

snmpTargetAddrRowStatus = MibTableColumn(snmpTargetAddrEntry.name + (9,)).setColumnInitializer(MibVariable((), RowStatus()).setMaxAccess('readcreate'))

# snmpTargetParamsTable

snmpTargetParamsTable = MibTable(snmpTargetObjects.name + (3,))

snmpTargetParamsEntry = MibTableRow(snmpTargetParamsTable.name + (1,)).setIndexNames((1, modName, 'snmpTargetParamsName'))
                                       
snmpTargetParamsName = MibTableColumn(snmpTargetParamsEntry.name + (1,)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueSizeConstraint(1, 32))).setMaxAccess('noaccess'))

snmpTargetParamsMPModel = MibTableColumn(snmpTargetParamsEntry.name + (2,)).setColumnInitializer(MibVariable((), SnmpMessageProcessingModel()).setMaxAccess('readcreate'))

snmpTargetParamsSecurityModel = MibTableColumn(snmpTargetParamsEntry.name + (3,)).setColumnInitializer(MibVariable((), SnmpSecurityModel().addConstraints(subtypes.ValueRangeConstraint(0, 2147483647))).setMaxAccess('readcreate'))

snmpTargetParamsSecurityName = MibTableColumn(snmpTargetParamsEntry.name + (4,)).setColumnInitializer(MibVariable((), SnmpAdminString()).setMaxAccess('readcreate'))

snmpTargetParamsSecurityLevel = MibTableColumn(snmpTargetParamsEntry.name + (5,)).setColumnInitializer(MibVariable((), SnmpSecurityLevel()).setMaxAccess('readcreate'))

snmpTargetParamsStorageType = MibTableColumn(snmpTargetParamsEntry.name + (6,)).setColumnInitializer(MibVariable((), StorageType(3)).setMaxAccess('readcreate'))

snmpTargetParamsRowStatus = MibTableColumn(snmpTargetParamsEntry.name + (7,)).setColumnInitializer(MibVariable((), RowStatus()).setMaxAccess('readcreate'))

snmpUnavailableContexts = MibVariable(
    snmpTargetObjects.name + (4,), Counter32()
    ).setMaxAccess('readonly')
snmpUnknownContexts = MibVariable(
    snmpTargetObjects.name + (5,), Counter32()
    ).setMaxAccess('readonly')

mibBuilder.exportSymbols(
    modName, snmpTargetMIB=snmpTargetMIB, snmpTargetObjects=snmpTargetObjects,
    snmpTargetConformance=snmpTargetConformance, SnmpTagValue=SnmpTagValue,
    SnmpTagList=SnmpTagList, snmpTargetSpinLock=snmpTargetSpinLock,
    snmpTargetAddrTable=snmpTargetAddrTable,
    snmpTargetAddrEntry=snmpTargetAddrEntry,
    snmpTargetAddrName=snmpTargetAddrName,
    snmpTargetAddrTDomain=snmpTargetAddrTDomain,
    snmpTargetAddrTAddress=snmpTargetAddrTAddress,
    snmpTargetAddrTimeout=snmpTargetAddrTimeout,
    snmpTargetAddrRetryCount=snmpTargetAddrRetryCount,
    snmpTargetAddrTagList=snmpTargetAddrTagList,
    snmpTargetAddrParams=snmpTargetAddrParams,
    snmpTargetAddrStorageType=snmpTargetAddrStorageType,
    snmpTargetAddrRowStatus=snmpTargetAddrRowStatus,
    snmpTargetParamsTable=snmpTargetParamsTable,
    snmpTargetParamsEntry=snmpTargetParamsEntry,
    snmpTargetParamsName=snmpTargetParamsName,
    snmpTargetParamsMPModel=snmpTargetParamsMPModel,
    snmpTargetParamsSecurityModel=snmpTargetParamsSecurityModel,
    snmpTargetParamsSecurityName=snmpTargetParamsSecurityName,
    snmpTargetParamsSecurityLevel=snmpTargetParamsSecurityLevel,
    snmpTargetParamsStorageType=snmpTargetParamsStorageType,
    snmpTargetParamsRowStatus=snmpTargetParamsRowStatus,
    snmpUnavailableContexts=snmpUnavailableContexts,
    snmpUnknownContexts=snmpUnknownContexts,
    )
