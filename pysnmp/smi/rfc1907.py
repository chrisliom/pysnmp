"""
   Management Information Base for SNMPv2 (RFC1907)

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ '' ]

from pysnmp.smi import rfc1902, rfc1903, rfc1904

class SnmpTrapOid(rfc1902.ObjectType):
    class Access(rfc1902.ObjectType.Access):
        initialValue = 'accessible-for-notify'
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class SimpleSyntax(rfc1902.SimpleSyntax):
                initialComponent = rfc1902.ObjectIdentifier
            initialComponent = SimpleSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBObjects(1).snmpTrap(4).snmpTrapOID(1)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpTrapEnterprise(rfc1902.ObjectType):
    class Access(rfc1902.ObjectType.Access):
        initialValue = 'accessible-for-notify'
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class SimpleSyntax(rfc1902.SimpleSyntax):
                initialComponent = rfc1902.ObjectIdentifier
            initialComponent = SimpleSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBObjects(1).snmpTrap(4).snmpTrapEnterprise(3)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpTrap(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBObjects(1).snmpTrap(4)'
    initialChildren = [ SnmpTrapOid, SnmpTrapEnterprise ]

class ColdStart(rfc1902.NotificationType):
    class NotificationName(rfc1902.NotificationName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBObjects(1).snmpTraps(5).coldStart(1)'

class WarmStart(rfc1902.NotificationType):
    class NotificationName(rfc1902.NotificationName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBObjects(1).snmpTraps(5).warmStart(2)'

class AuthenticationFailure(rfc1902.NotificationType):
    class NotificationName(rfc1902.NotificationName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBObjects(1).snmpTraps(5).authenticationFailure(3)'

class SnmpTraps(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBObjects(1).snmpTraps(5)'
    initialChildren = [ ColdStart, WarmStart, AuthenticationFailure ]

class SnmpSetSerialNo(rfc1902.ObjectType):
    class Access(rfc1902.ObjectType.Access):
        initialValue = 'read-write'
    class DisplayPart(rfc1903.TestAndIncr.DisplayPart): pass
    class Syntax(rfc1903.TestAndIncr.Syntax): pass
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBObjects(1).snmpSet(6).snmpSetSerialNo(1)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpSet(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBObjects(1).snmpSet(6)'
    initialChildren = [ SnmpSetSerialNo ]

class SnmpMibObjects(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBObjects(1)'
    initialChildren = [ SnmpTrap, SnmpTraps, SnmpSet ]

class SysDescr(rfc1902.ObjectType):
    class DisplayPart(rfc1903.DisplayString.DisplayPart): pass
    class Syntax(rfc1903.DisplayString.Syntax): pass
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).system(1).sysDescr(1)'
    fixedComponents = [ Syntax, ObjectName ]

class SysObjectId(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class SimpleSyntax(rfc1902.SimpleSyntax):
                class ObjectIdentifier(rfc1902.ObjectIdentifier): pass
                initialComponent = ObjectIdentifier
            initialComponent = SimpleSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).system(1).sysObjectID(2)'
    fixedComponents = [ Syntax, ObjectName ]

class SysUpTime(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                class TimeTicks(rfc1902.TimeTicks): pass
                initialComponent = TimeTicks
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).system(1).sysUpTime(3)'
    fixedComponents = [ Syntax, ObjectName ]

class SysContact(rfc1902.ObjectType):
    class DisplayPart(rfc1903.DisplayString.DisplayPart): pass
    class Syntax(rfc1903.DisplayString.Syntax): pass
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).system(1).sysContact(4)'
    fixedComponents = [ Syntax, ObjectName ]

class SysName(rfc1902.ObjectType):
    class DisplayPart(rfc1903.DisplayString.DisplayPart): pass
    class Syntax(rfc1903.DisplayString.Syntax): pass
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).system(1).sysName(5)'
    fixedComponents = [ Syntax, ObjectName ]

class SysLocation(rfc1902.ObjectType):
    class DisplayPart(rfc1903.DisplayString.DisplayPart): pass
    class Syntax(rfc1903.DisplayString.Syntax): pass
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).system(1).sysLocation(6)'
    fixedComponents = [ Syntax, ObjectName ]

class SysServices(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class SimpleSyntax(rfc1902.SimpleSyntax):
                class Integer(rfc1902.Integer):
                    valueRangeConstraint = (0, 127)
                initialComponent = Integer
            initialComponent = SimpleSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).system(1).sysServices(7)'
    fixedComponents = [ Syntax, ObjectName ]

class SysOrLastChange(rfc1902.ObjectType):
    class DisplayPart(rfc1903.TimeStamp.DisplayPart): pass
    class Syntax(rfc1903.TimeStamp.Syntax): pass
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).system(1).sysORLastChange(8)'
    fixedComponents = [ Syntax, ObjectName ]

# object resource information

class SysOrUpTime(rfc1902.ObjectType):
    class DisplayPart(rfc1903.TimeStamp.DisplayPart): pass
    class Syntax(rfc1903.TimeStamp.Syntax): pass
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).system(1).sysORTable(9).sysOREntry(1).sysORUpTime(4)'
    fixedComponents = [ Syntax, ObjectName ]

class SysOrDescr(rfc1902.ObjectType):
    class DisplayPart(rfc1903.DisplayString.DisplayPart): pass
    class Syntax(rfc1903.DisplayString.Syntax): pass
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).system(1).sysORTable(9).sysOREntry(1).sysORDescr(3)'
    fixedComponents = [ Syntax, ObjectName ]

class SysOrId(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class SimpleSyntax(rfc1902.SimpleSyntax):
                initialComponent = rfc1902.ObjectIdentifier
            initialComponent = SimpleSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).system(1).sysORTable(9).sysOREntry(1).sysORID(2)'
    fixedComponents = [ Syntax, ObjectName ]

class SysOrIndex(rfc1902.ObjectType):
    class Access(rfc1902.ObjectType.Access):
        initialValue = 'not-accessible'
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class SimpleSyntax(rfc1902.SimpleSyntax):
                class Integer(rfc1902.Integer):
                    valueRangeConstraint = (1, 2147483647)
                initialComponent = Integer
            initialComponent = SimpleSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).system(1).sysORTable(9).sysOREntry(1).sysORIndex(1)'
    fixedComponents = [ Syntax, ObjectName ]

class SysOrEntry(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class TableSyntax(rfc1902.ObjectSyntax.TableSyntax):
                class SysOrEntryType(rfc1902.Sequence):
                    fixedNames = [ 'sysORIndex', 'sysORID', 'sysORDescr',
                                   'sysORUpTime' ]
                    fixedComponents = [ SysOrIndex, SysOrId, SysOrDescr,
                                        SysOrUpTime ]
                initialComponent = SysOrEntryType
            initialComponent = TableSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).system(1).sysORTable(9).sysOREntry(1)'
        initialChildren = [ SysOrIndex, SysOrId, SysOrDescr ]
    fixedComponents = [ Syntax, ObjectName ]

class SysOrTable(rfc1902.ObjectType):
    class Access(rfc1902.ObjectType.Access):
        initialValue = 'not-accessible'
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class TableSyntax(rfc1902.ObjectSyntax.TableSyntax):
                class SysOrEntries(rfc1902.SequenceOf):
                    protoComponent = SysOrEntry
                initialComponent = SysOrEntries
            initialComponent = TableSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).system(1).sysORTable(8)'
        initialChildren = [ SysOrEntry ]
    fixedComponents = [ Syntax, ObjectName ]

# The SNMP group

class SnmpInPkts(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpInPkts(1)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpInBadVersions(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpInBadVersions(3)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpInBadCommunityNames(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpInBadCommunityNames(4)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpInBadCommunityUses(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpInBadCommunityUses(5)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpInAsnParseErrs(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpInASNParseErrs(6)'
    fixedComponents = [ Syntax, ObjectName ]
    
class SnmpEnableAuthenTraps(rfc1902.ObjectType):
    class Access(rfc1902.ObjectType.Access):
        initialValue = 'read-write'
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class SimpleSyntax(rfc1902.SimpleSyntax):
                class Integer(rfc1902.Integer):
                    singleValueConstraint = [1, 2]
                    initialValue = 1
                initialComponent = Integer
            initialComponent = SimpleSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpEnableAuthenTraps(130)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpSilentDrops(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpSilentDrops(31)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpProxyDrops(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpProxyDrops(32)'
    fixedComponents = [ Syntax, ObjectName ]

# definitions in RFC 1213 made obsolete by the inclusion of a
# subset of the snmp group in this MIB

class SnmpOutPkts(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpOutPkts(2)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpInTooBigs(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpInTooBigs(8)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpInNoSuchNames(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpInNoSuchNames(9)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpInBadValues(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpInBadValues(10)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpInReadOnlys(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpInReadOnlys(11)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpInGenErrs(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpInGenErrs(12)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpInTotalReqVars(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpInTotalReqVars(13)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpInTotalSetVars(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpInTotalSetVars(14)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpInGetRequests(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpInGetRequests(15)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpInGetNexts(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpInGetNexts(16)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpInSetRequests(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpInSetRequests(17)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpInGetResponses(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpInGetResponses(18)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpInTraps(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpInTraps(19)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpOutTooBigs(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpOutTooBigs(20)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpOutNoSuchNames(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpOutNoSuchNames(21)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpOutBadValues(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpOutBadValues(22)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpOutGenErrs(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpOutGenErrs(24)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpOutGetRequests(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpOutGetRequests(25)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpOutGetNexts(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpOutGetNexts(26)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpOutSetRequests(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).SnmpOutSetRequests(27)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpOutGetResponses(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpOutGetResponses(28)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpOutTraps(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                initialComponent = rfc1902.Counter32
            initialComponent = ApplicationSyntax
        initialComponent = ObjectSyntax
    class Status(rfc1902.ObjectType.Status):
        initialValue = "obsolete"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpOutTraps(29)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpObsoleteGroup(rfc1904.ObjectGroup):
    class ObjectsPart(rfc1904.ObjectGroup.ObjectsPart):
        initialValue = [ SnmpOutPkts, SnmpInTooBigs, SnmpInNoSuchNames,
                         SnmpInBadValues, SnmpInReadOnlys, SnmpInGenErrs,
                         SnmpInTotalReqVars, SnmpInTotalSetVars,
                         SnmpInGetRequests, SnmpInGetNexts, SnmpInSetRequests,
                         SnmpInGetResponses, SnmpInTraps, SnmpOutTooBigs,
                         SnmpOutNoSuchNames, SnmpOutBadValues, SnmpOutGenErrs,
                         SnmpOutGetRequests, SnmpOutGetNexts,
                         SnmpOutSetRequests, SnmpOutGetResponses, SnmpOutTraps]

    class ObjectIdentifier(rfc1904.ObjectGroup.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBConformance(2).snmpMIBGroups(2).snmpObsoleteGroup(10)'
    fixedComponents = [ ObjectsPart, ObjectIdentifier ]

class Snmp(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11)'
    initialChildren = [ SnmpInPkts, SnmpInBadVersions,
                        SnmpInBadCommunityNames, SnmpInBadCommunityUses,
                        SnmpInAsnParseErrs, SnmpEnableAuthenTraps,
                        SnmpSilentDrops, SnmpProxyDrops,
                        SnmpOutPkts, SnmpInTooBigs, SnmpInNoSuchNames,
                        SnmpInBadValues, SnmpInReadOnlys,
                        SnmpInGenErrs,  SnmpInTotalReqVars,
                        SnmpInTotalSetVars, SnmpInGetRequests,
                        SnmpInGetNexts, SnmpInSetRequests,
                        SnmpInGetResponses, SnmpInTraps,
                        SnmpOutTooBigs, SnmpOutNoSuchNames,
                        SnmpOutBadValues, SnmpOutGenErrs,
                        SnmpOutGetRequests, SnmpOutGetNexts,
                        SnmpOutSetRequests, SnmpOutGetResponses,
                        SnmpOutTraps ]

class System(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).system(1)'
    initialChildren = [ SysDescr, SysObjectId, SysUpTime, SysContact,
                        SysName, SysServices, SysOrLastChange, SysOrUpTime ]

class SnmpGroup(rfc1904.ObjectGroup):
    class ObjectsPart(rfc1904.ObjectGroup.ObjectsPart):
        initialValue = [ SnmpInPkts, SnmpInBadVersions, SnmpInAsnParseErrs,
                         SnmpSilentDrops, SnmpProxyDrops,
                         SnmpEnableAuthenTraps ]

    class ObjectIdentifier(rfc1904.ObjectGroup.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBConformance(2).snmpMIBGroups(2).snmpGroup(8)'
    fixedComponents = [ ObjectsPart, ObjectIdentifier ]

class SnmpCommunityGroup(rfc1904.ObjectGroup):
    class ObjectsPart(rfc1904.ObjectGroup.ObjectsPart):
        initialValue = [ SnmpInBadCommunityNames, SnmpInBadCommunityUses ]

    class ObjectIdentifier(rfc1904.ObjectGroup.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBConformance(2).snmpMIBGroups(2).snmpCommunityGroup(9)'
    fixedComponents = [ ObjectsPart, ObjectIdentifier ]

class SnmpSetGroup(rfc1904.ObjectGroup):
    class ObjectsPart(rfc1904.ObjectGroup.ObjectsPart):
        initialValue = [ SnmpSetSerialNo ]

    class ObjectIdentifier(rfc1904.ObjectGroup.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBConformance(2).snmpMIBGroups(2).snmpSetSerialNo(5)'
    fixedComponents = [ ObjectsPart, ObjectIdentifier ]

class SystemGroup(rfc1904.ObjectGroup):
    class ObjectsPart(rfc1904.ObjectGroup.ObjectsPart):
        initialValue = [ SysDescr, SysObjectId, SysUpTime, SysContact,
                         SysName, SysLocation, SysServices, SysOrLastChange,
                         SysOrId, SysOrUpTime, SysOrDescr ]

    class ObjectIdentifier(rfc1904.ObjectGroup.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBConformance(2).snmpMIBGroups(2).systemGroup(6)'
    fixedComponents = [ ObjectsPart, ObjectIdentifier ]

class SnmpBasicNotificationsGroup(rfc1904.NotificationGroup):
    class NotificationsPart(rfc1904.NotificationGroup.NotificationsPart):
        initialValue = [ ColdStart, AuthenticationFailure ]

    class ObjectIdentifier(rfc1904.ObjectGroup.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBConformance(2).snmpMIBGroups(2).snmpBasicNotificationsGroup(7)'
    fixedComponents = [ NotificationsPart, ObjectIdentifier ]

class SnmpMibGroups(rfc1902.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBConformance(2).snmpMIBGroups(2)'
        initialChildren = [ SnmpGroup, SnmpCommunityGroup, SnmpSetGroup,
                            SystemGroup, SnmpBasicNotificationsGroup,
                            SnmpObsoleteGroup ]

class SnmpBasicCompliance(rfc1904.ModuleCompliance):
    class ModulePart(rfc1904.ModuleCompliance.ModulePart):
        class Modules(rfc1904.ModuleCompliance.ModulePart.Modules):
            class Module(rfc1904.ModuleCompliance.ModulePart.Modules.Module):
                class ModuleName(rfc1904.ModuleCompliance.ModulePart.Modules.Module.ModuleName):
                    class ModuleIdentifier(rfc1904.ModuleCompliance.ModulePart.Modules.Module.ModuleName.ModuleIdentifier):
# XXX forward reference
#                        initialComponent = SnmpMib.ObjectIdentifier
                        pass
                    initialComponent = ModuleIdentifier
                class MandatoryPart(rfc1904.ModuleCompliance.ModulePart.Modules.Module.MandatoryPart):
                    class Groups(rfc1904.ModuleCompliance.ModulePart.Modules.Module.MandatoryPart.Groups):
                        initialValue = [ SnmpGroup.ObjectIdentifier, SnmpSetGroup.ObjectIdentifier, SystemGroup.ObjectIdentifier, SnmpBasicNotificationsGroup.ObjectIdentifier ]
                    initialValue = Groups
                fixedComponents = [ ModuleName, MandatoryPart, rfc1904.ModuleCompliance.ModulePart.Modules.Module.CompliancePart ]
            initialValue = Module
        initialComponent = Modules
        
    class ObjectIdentifier(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBConformance(2).snmpMIBCompliances(1).snmpBasicCompliance(2)'
    fixedComponents = [ ModulePart, ObjectIdentifier ]

class SnmpMibCompliances(rfc1902.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBConformance(2).snmpMIBCompliances(1)'
        initialChildren = [ SnmpBasicCompliance ]
        
class SnmpMibConformance(rfc1902.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1).snmpMIBConformance(2)'
        initialChildren = [ SnmpMibCompliances, SnmpMibGroups ]

class SnmpMib(rfc1902.ModuleIdentity):
    class LastUpdated(rfc1902.ModuleIdentity.LastUpdated):
        initialValue = "9511090000Z"
    class Organization(rfc1902.ModuleIdentity.Organization):
        initialValue = "IETF SNMPv2 Working Group"
    class RevisionPart(rfc1902.ModuleIdentity.RevisionPart):
        class Revisions(rfc1902.ModuleIdentity.RevisionPart.Revisions):
            class Revision(rfc1902.ModuleIdentity.RevisionPart.Revisions.Revision): initialValue = "9304010000Z"
            initialValue = [ Revision ]
        initialComponent = Revisions
    class ObjectIdentifier(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMIB(1)'
        initialChilden = [ SnmpMibObjects, SnmpMibConformance ]
    fixedComponents = [ ObjectIdentifier ]

if __name__ == '__main__':
    from pysnmp.asn1 import oidtree
    import profile
    
    t = oidtree.Root()
#    t.attachNode(SnmpEngineId()['value'], SnmpEngineId())
    t.attachNode(Snmp())
    t.strNode()
    def a():
        for i in range(10):
            t.searchNode('.iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).snmp(11).snmpOutPkts(2)')
    profile.run('a()')
