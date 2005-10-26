from sys import version
from time import time
from pysnmp import majorVersionId

( MibScalarInstance,
  TimeTicks) = mibBuilder.importSymbols(
    'SNMPv2-SMI',
    'MibScalarInstance',
    'TimeTicks'
    )

( sysDescr,
  sysObjectID,
  sysUpTime,
  sysContact,
  sysName,
  sysLocation,
  sysServices,
  sysORLastChange,
  snmpInPkts,
  snmpOutPkts,
  snmpInBadVersions,
  snmpInBadCommunityNames,
  snmpInBadCommunityUses,
  snmpInASNParseErrs,
  snmpInTooBigs,
  snmpInNoSuchNames,
  snmpInBadValues,
  snmpInReadOnlys,
  snmpInGenErrs,
  snmpInTotalReqVars,
  snmpInTotalSetVars,
  snmpInGetRequests,
  snmpInGetNexts,
  snmpInSetRequests,
  snmpInGetResponses,
  snmpInTraps,
  snmpOutTooBigs,
  snmpOutNoSuchNames,
  snmpOutBadValues,
  snmpOutGenErrs,
  snmpOutSetRequests,
  snmpOutGetResponses,
  snmpOutTraps,
  snmpEnableAuthenTraps,
  snmpSilentDrops,
  snmpProxyDrops,
  snmpSetSerialNo ) = mibBuilder.importSymbols(
    'SNMPv2-MIB',
    'sysDescr',
    'sysObjectID',
    'sysUpTime',
    'sysContact',
    'sysName',
    'sysLocation',
    'sysServices',
    'sysORLastChange',
    'snmpInPkts',
    'snmpOutPkts',
    'snmpInBadVersions',
    'snmpInBadCommunityNames',
    'snmpInBadCommunityUses',
    'snmpInASNParseErrs',
    'snmpInTooBigs',
    'snmpInNoSuchNames',
    'snmpInBadValues',
    'snmpInReadOnlys',
    'snmpInGenErrs',
    'snmpInTotalReqVars',
    'snmpInTotalSetVars',
    'snmpInGetRequests',
    'snmpInGetNexts',
    'snmpInSetRequests',
    'snmpInGetResponses',
    'snmpInTraps',
    'snmpOutTooBigs',
    'snmpOutNoSuchNames',
    'snmpOutBadValues',
    'snmpOutGenErrs',
    'snmpOutSetRequests',
    'snmpOutGetResponses',
    'snmpOutTraps',
    'snmpEnableAuthenTraps',
    'snmpSilentDrops',
    'snmpProxyDrops',
    'snmpSetSerialNo'
    )

__sysDescr = MibScalarInstance(sysDescr.name, (0,), sysDescr.syntax.clone("PySNMP engine version %s, Python %s" % (majorVersionId, version)))
__sysObjectID = MibScalarInstance(sysObjectID.name, (0,), sysObjectID.syntax.clone((1,3,6,1,4,1,20408)))

class SysUpTime(TimeTicks):
    birthday = time()
    def clone(self, value=None, tagSet=None, subtypeSpec=None):
        if value is None:
            value = int(time()-self.birthday)*100
        return TimeTicks.clone(self, value)

__sysUpTime = MibScalarInstance(sysUpTime.name, (0,), sysUpTime.syntax.clone(SysUpTime()))
__sysContact = MibScalarInstance(sysContact.name, (0,), sysContact.syntax)
__sysName = MibScalarInstance(sysName.name, (0,), sysName.syntax)
__sysLocation = MibScalarInstance(sysLocation.name, (0,), sysLocation.syntax)
__sysServices = MibScalarInstance(sysServices.name, (0,), sysServices.syntax)
__sysORLastChange = MibScalarInstance(sysORLastChange.name, (0,), sysORLastChange.syntax)
__snmpInPkts = MibScalarInstance(snmpInPkts.name, (0,), snmpInPkts.syntax)
__snmpOutPkts = MibScalarInstance(snmpOutPkts.name, (0,), snmpOutPkts.syntax)
__snmpInBadVersions = MibScalarInstance(snmpInBadVersions.name, (0,), snmpInBadVersions.syntax)
__snmpInBadCommunityNames = MibScalarInstance(snmpInBadCommunityNames.name, (0,), snmpInBadCommunityNames.syntax)
__snmpInBadCommunityUses = MibScalarInstance(snmpInBadCommunityUses.name, (0,), snmpInBadCommunityUses.syntax)
__snmpInASNParseErrs = MibScalarInstance(snmpInASNParseErrs.name, (0,), snmpInASNParseErrs.syntax)
__snmpInTooBigs = MibScalarInstance(snmpInTooBigs.name, (0,), snmpInTooBigs.syntax)
__snmpInNoSuchNames = MibScalarInstance(snmpInNoSuchNames.name, (0,), snmpInNoSuchNames.syntax)
__snmpInBadValues = MibScalarInstance(snmpInBadValues.name, (0,), snmpInBadValues.syntax)
__snmpInReadOnlys = MibScalarInstance(snmpInReadOnlys.name, (0,), snmpInReadOnlys.syntax)
__snmpInGenErrs = MibScalarInstance(snmpInGenErrs.name, (0,), snmpInGenErrs.syntax)
__snmpInTotalReqVars = MibScalarInstance(snmpInTotalReqVars.name, (0,), snmpInTotalReqVars.syntax)
__snmpInTotalSetVars = MibScalarInstance(snmpInTotalSetVars.name, (0,), snmpInTotalSetVars.syntax)
__snmpInGetRequests = MibScalarInstance(snmpInGetRequests.name, (0,), snmpInGetRequests.syntax)
__snmpInGetNexts = MibScalarInstance(snmpInGetNexts.name, (0,), snmpInGetNexts.syntax)
__snmpInSetRequests = MibScalarInstance(snmpInSetRequests.name, (0,), snmpInSetRequests.syntax)
__snmpInGetResponses = MibScalarInstance(snmpInGetResponses.name, (0,), snmpInGetResponses.syntax)
__snmpInTraps = MibScalarInstance(snmpInTraps.name, (0,), snmpInTraps.syntax)
__snmpOutTooBigs = MibScalarInstance(snmpOutTooBigs.name, (0,), snmpOutTooBigs.syntax)
__snmpOutNoSuchNames = MibScalarInstance(snmpOutNoSuchNames.name, (0,), snmpOutNoSuchNames.syntax)
__snmpOutBadValues = MibScalarInstance(snmpOutBadValues.name, (0,), snmpOutBadValues.syntax)
__snmpOutGenErrs = MibScalarInstance(snmpOutGenErrs.name, (0,), snmpOutGenErrs.syntax)
__snmpOutSetRequests = MibScalarInstance(snmpOutSetRequests.name, (0,), snmpOutSetRequests.syntax)
__snmpOutGetResponses = MibScalarInstance(snmpOutGetResponses.name, (0,), snmpOutGetResponses.syntax)
__snmpOutTraps = MibScalarInstance(snmpOutTraps.name, (0,), snmpOutTraps.syntax)
__snmpEnableAuthenTraps = MibScalarInstance(snmpEnableAuthenTraps.name, (0,), snmpEnableAuthenTraps.syntax)
__snmpSilentDrops = MibScalarInstance(snmpSilentDrops.name, (0,), snmpSilentDrops.syntax)
__snmpProxyDrops = MibScalarInstance(snmpProxyDrops.name, (0,), snmpProxyDrops.syntax)
__snmpSetSerialNo = MibScalarInstance(snmpSetSerialNo.name, (0,), snmpSetSerialNo.syntax)

mibBuilder.exportSymbols(
    "__SNMPv2-MIB",
    sysDescr = __sysDescr,
    sysObjectID = __sysObjectID,
    sysUpTime = __sysUpTime,
    sysContact = __sysContact,
    sysName = __sysName,
    sysLocation = __sysLocation,
    sysServices = __sysServices,
    sysORLastChange = __sysORLastChange,
    snmpInPkts = __snmpInPkts,
    snmpOutPkts = __snmpOutPkts,
    snmpInBadVersions = __snmpInBadVersions,
    snmpInBadCommunityNames = __snmpInBadCommunityNames,
    snmpInBadCommunityUses = __snmpInBadCommunityUses,
    snmpInASNParseErrs = __snmpInASNParseErrs,
    snmpInTooBigs = __snmpInTooBigs,
    snmpInNoSuchNames = __snmpInNoSuchNames,
    snmpInBadValues = __snmpInBadValues,
    snmpInReadOnlys = __snmpInReadOnlys,
    snmpInGenErrs = __snmpInGenErrs,
    snmpInTotalReqVars = __snmpInTotalReqVars,
    snmpInTotalSetVars = __snmpInTotalSetVars,
    snmpInGetRequests = __snmpInGetRequests,
    snmpInGetNexts = __snmpInGetNexts,
    snmpInSetRequests = __snmpInSetRequests,
    snmpInGetResponses = __snmpInGetResponses,
    snmpInTraps = __snmpInTraps,
    snmpOutTooBigs = __snmpOutTooBigs,
    snmpOutNoSuchNames = __snmpOutNoSuchNames,
    snmpOutBadValues = __snmpOutBadValues,
    snmpOutGenErrs = __snmpOutGenErrs,
    snmpOutSetRequests = __snmpOutSetRequests,
    snmpOutGetResponses = __snmpOutGetResponses,
    snmpOutTraps = __snmpOutTraps,
    snmpEnableAuthenTraps = __snmpEnableAuthenTraps,
    snmpSilentDrops = __snmpSilentDrops,
    snmpProxyDrops = __snmpProxyDrops,
    snmpSetSerialNo = __snmpSetSerialNo
    )
