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
    ).setAccess('readwrite')

# snmpTargetAddrTable

snmpTargetAddrTable = MibTable(snmpTargetObjects.name + (2,))

snmpTargetAddrEntry = MibTableRow(snmpTargetAddrTable.name + (1,)).setIndexNames((1, modName, 'snmpTargetAddrTable'))

snmpTargetAddrName = MibTableColumn(snmpTargetAddrEntry.name + (1,)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueRangeConstraint(1, 32))).setAccess('noaccess'))

snmpTargetAddrTDomain = MibTableColumn(snmpTargetAddrEntry.name + (2,)).setColumnInitializer(MibVariable((), TDomain()).setAccess('readcreate'))

snmpTargetAddrTAddress = MibTableColumn(snmpTargetAddrEntry.name + (3,)).setColumnInitializer(MibVariable((), TAddress()).setAccess('readcreate'))

snmpTargetAddrTimeout = MibTableColumn(snmpTargetAddrEntry.name + (4,)).setColumnInitializer(MibVariable((), TimeInterval(1500)).setAccess('readcreate'))

snmpTargetAddrRetryCount = MibTableColumn(snmpTargetAddrEntry.name + (5,)).setColumnInitializer(MibVariable((), Integer32(3).addConstraints(subtypes.ValueRangeConstraint(0, 255))).setAccess('readcreate'))

snmpTargetAddrTagList = MibTableColumn(snmpTargetAddrEntry.name + (6,)).setColumnInitializer(MibVariable((), SnmpTagList("")).setAccess('readcreate'))

snmpTargetAddrParams = MibTableColumn(snmpTargetAddrEntry.name + (7,)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueSizeConstraint(1, 32))).setAccess('readcreate'))

snmpTargetAddrStorageType = MibTableColumn(snmpTargetAddrEntry.name + (8,)).setColumnInitializer(MibVariable((), StorageType(3)).setAccess('readcreate'))

snmpTargetAddrRowStatus = MibTableColumn(snmpTargetAddrEntry.name + (9,)).setColumnInitializer(MibVariable((), RowStatus()).setAccess('readcreate'))

# snmpTargetParamsTable

snmpTargetParamsTable = MibTable(snmpTargetObjects.name + (3,))

snmpTargetParamsEntry = MibTableRow(snmpTargetParamsTable.name + (1,)).setIndexNames((1, modName, 'snmpTargetParamsName'))
                                       
snmpTargetParamsName = MibTableColumn(snmpTargetParamsEntry.name + (1,)).setColumnInitializer(MibVariable((), SnmpAdminString().addConstraints(subtypes.ValueSizeConstraint(1, 32))).setAccess('noaccess'))

snmpTargetParamsMPModel = MibTableColumn(snmpTargetParamsEntry.name + (2,)).setColumnInitializer(MibVariable((), SnmpMessageProcessingModel()).setAccess('readcreate'))

snmpTargetParamsSecurityModel = MibTableColumn(snmpTargetParamsEntry.name + (3,)).setColumnInitializer(MibVariable((), SnmpSecurityModel().addConstraints(subtypes.ValueRangeConstraint(0, 2147483647))).setAccess('readcreate'))

snmpTargetParamsSecurityName = MibTableColumn(snmpTargetParamsEntry.name + (4,)).setColumnInitializer(MibVariable((), SnmpAdminString()).setAccess('readcreate'))

snmpTargetParamsSecurityLevel = MibTableColumn(snmpTargetParamsEntry.name + (5,)).setColumnInitializer(MibVariable((), SnmpSecurityLevel()).setAccess('readcreate'))

snmpTargetParamsStorageType = MibTableColumn(snmpTargetParamsEntry.name + (6,)).setColumnInitializer(MibVariable((), StorageType(3)).setAccess('readcreate'))

snmpTargetParamsRowStatus = MibTableColumn(snmpTargetParamsEntry.name + (7,)).setColumnInitializer(MibVariable((), RowStatus()).setAccess('readcreate'))

snmpUnavailableContexts = MibVariable(
    snmpTargetObjects.name + (4,), Counter32()
    ).setAccess('readonly')
snmpUnknownContexts = MibVariable(
    snmpTargetObjects.name + (5,), Counter32()
    ).setAccess('readonly')

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
