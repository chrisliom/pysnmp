"""
   The management information definitions for the SNMP User-based Security
   Model (RFC3414)

   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
from pysnmp.smi import rfc1902, rfc1903, rfc1904, rfc3411

class UsmNoAuthProtocol(rfc1902.ObjectIdentity):
    class ObjectIdentifier(rfc1902.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10).snmpFrameworkAdmin(1).snmpAuthProtocols(1).usmNoAuthProtocol(1)'
    fixedComponents = [ ObjectIdentifier ]

class UsmHMACMD5AuthProtocol(rfc1902.ObjectIdentity):
    class ObjectIdentifier(rfc1902.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10).snmpFrameworkAdmin(1).snmpAuthProtocols(1).usmHMACMD5AuthProtocol(2)'
    fixedComponents = [ ObjectIdentifier ]

class UsmHMACSHAAuthProtocol(rfc1902.ObjectIdentity):
    class ObjectIdentifier(rfc1902.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10).snmpFrameworkAdmin(1).snmpAuthProtocols(1).usmHMACSHAAuthProtocol(3)'
    fixedComponents = [ ObjectIdentifier ]

class UsmNoPrivProtocol(rfc1902.ObjectIdentity):
    class ObjectIdentifier(rfc1902.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10).snmpFrameworkAdmin(1).snmpPrivProtocols(2).usmNoPrivProtocol(1)'
    fixedComponents = [ ObjectIdentifier ]

class UsmDESPrivProtocol(rfc1902.ObjectIdentity):
    class ObjectIdentifier(rfc1902.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10).snmpFrameworkAdmin(1).snmpPrivProtocols(2).usmDESPrivProtocol(2)'
    fixedComponents = [ ObjectIdentifier ]

class KeyChange(rfc1903.TextualConvention):
    class Syntax(rfc1903.TextualConvention.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class SimpleSyntax(rfc1902.SimpleSyntax):
                class String(rfc1902.OctetString): pass
                choiceComponents = [ String ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
    fixedComponents = [ Syntax ]
    
class UsmStatsUnsupportedSecLevels(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                class Value(rfc1902.Counter32):
                    initialValue = 0
                choiceComponents = [ Value ]
                initialComponent = choiceComponents[0]
            choiceComponents = [ ApplicationSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmStats(1).usmStatsUnsupportedSecLevels(1)'
    fixedComponents = [ Syntax, ObjectName ]
                    
class UsmStatsNotInTimeWindows(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                class Value(rfc1902.Counter32):
                    initialValue = 0
                choiceComponents = [ Value ]
                initialComponent = choiceComponents[0]
            choiceComponents = [ ApplicationSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmStats(1).usmStatsNotInTimeWindows(2)'
    fixedComponents = [ Syntax, ObjectName ]

class UsmStatsUnknownUserNames(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                class Value(rfc1902.Counter32):
                    initialValue = 0
                choiceComponents = [ Value ]
                initialComponent = choiceComponents[0]
            choiceComponents = [ ApplicationSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmStats(1).usmStatsUnknownUserNames(3)'
    fixedComponents = [ Syntax, ObjectName ]

class UsmStatsUnknownEngineIDs(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                class Value(rfc1902.Counter32):
                    initialValue = 0
                choiceComponents = [ Value ]
                initialComponent = choiceComponents[0]
            choiceComponents = [ ApplicationSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmStats(1).usmStatsUnknownEngineIDs(4)'
    fixedComponents = [ Syntax, ObjectName ]

class UsmStatsWrongDigests(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                class Value(rfc1902.Counter32):
                    initialValue = 0
                choiceComponents = [ Value ]
                initialComponent = choiceComponents[0]
            choiceComponents = [ ApplicationSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmStats(1).usmStatsWrongDigests(5)'
    fixedComponents = [ Syntax, ObjectName ]

class UsmStatsDecryptionErrors(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class ApplicationSyntax(rfc1902.ApplicationSyntax):
                class Value(rfc1902.Counter32):
                    initialValue = 0
                choiceComponents = [ Value ]
                initialComponent = choiceComponents[0]
            choiceComponents = [ ApplicationSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmStats(1).usmStatsDecryptionErrors(6)'
    fixedComponents = [ Syntax, ObjectName ]

class UsmStats(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmStats(1)'
    initialChildren = [ UsmStatsUnsupportedSecLevels,
                        UsmStatsNotInTimeWindows,
                        UsmStatsUnknownUserNames,
                        UsmStatsUnknownEngineIDs,
                        UsmStatsWrongDigests,
                        UsmStatsDecryptionErrors ]

class UsmUserSpinLock(rfc1902.ObjectType):
    class Access(rfc1902.ObjectType.Access):
        initialValue = "read-write"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmUser(2).UsmUserSpinLock(1)'
    fixedComponents = [ rfc1903.TestAndIncr.Syntax, ObjectName ]

class UsmUserStatus(rfc1902.ObjectType):
    class Access(rfc1902.ObjectType.Access):
        initialValue = "read-create"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmUser(2).usmUserTable(2).UsmUserEntry(1).usmUserStatus(13)'
    fixedComponents = [ rfc1903.RowStatus.Syntax, ObjectName ]

class UsmUserStorageType(rfc1902.ObjectType):
    class Access(rfc1902.ObjectType.Access):
        initialValue = "read-create"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmUser(2).usmUserTable(2).UsmUserEntry(1).usmUserStorageType(12)'
    fixedComponents = [ rfc1903.StorageType.Syntax, ObjectName ]

class UsmUserPublic(rfc1902.ObjectType):
    class Syntax(rfc1903.TextualConvention.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class SimpleSyntax(rfc1902.SimpleSyntax):
                class String(rfc1902.OctetString):
                    sizeConstraint = (0, 32)
                choiceComponents = [ String ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
    class Access(rfc1902.ObjectType.Access):
        initialValue = "read-create"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmUser(2).usmUserTable(2).UsmUserEntry(1).usmUserPublic(11)'
    fixedComponents = [ Syntax, ObjectName ]

class UsmUserOwnPrivKeyChange(rfc1902.ObjectType):
    class Access(rfc1902.ObjectType.Access):
        initialValue = "read-create"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmUser(2).usmUserTable(2).UsmUserEntry(1).usmUserOwnPrivKeyChange(10)'
    fixedComponents = [ KeyChange.Syntax, ObjectName ]

class UsmUserPrivKeyChange(rfc1902.ObjectType):
    class Access(rfc1902.ObjectType.Access):
        initialValue = "read-create"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmUser(2).usmUserTable(2).UsmUserEntry(1).usmUserPrivKeyChange(9)'
    fixedComponents = [ KeyChange.Syntax, ObjectName ]

class UsmUserPrivProtocol(rfc1902.ObjectType):
    class Syntax(rfc1903.AutonomousType):
        class Syntax(rfc1903.AutonomousType.Syntax):
            class ObjectSyntax(rfc1902.ObjectSyntax):
                class SimpleSyntax(rfc1902.SimpleSyntax):
                    initialComponent = UsmNoPrivProtocol.ObjectIdentifier
                choiceComponents = [ SimpleSyntax ]
                initialComponent = choiceComponents[0]
            choiceComponents = [ ObjectSyntax ]
            initialComponent = choiceComponents[0]
        fixedComponents = [ Syntax ]
    class Access(rfc1902.ObjectType.Access):
        initialValue = "read-create"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmUser(2).usmUserTable(2).UsmUserEntry(1).usmUserPrivProtocol(8)'
    fixedComponents = [ rfc1903.RowPointer.Syntax, ObjectName ]

class UsmUserOwnAuthKeyChange(rfc1902.ObjectType):
    class Access(rfc1902.ObjectType.Access):
        initialValue = "read-create"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmUser(2).usmUserTable(2).UsmUserEntry(1).usmUserOwnAuthKeyChange(7)'
    fixedComponents = [ KeyChange.Syntax, ObjectName ]

class UsmUserOwnAuthKeyChange(rfc1902.ObjectType):
    class Access(rfc1902.ObjectType.Access):
        initialValue = "read-create"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmUser(2).usmUserTable(2).UsmUserEntry(1).usmUserOwnAuthKeyChange(7)'
    fixedComponents = [ KeyChange.Syntax, ObjectName ]

class UsmUserAuthKeyChange(rfc1902.ObjectType):
    class Access(rfc1902.ObjectType.Access):
        initialValue = "read-create"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmUser(2).usmUserTable(2).UsmUserEntry(1).usmUserAuthKeyChange(6)'
    fixedComponents = [ KeyChange.Syntax, ObjectName ]

class UsmUserAuthProtocol(rfc1902.ObjectType):
    class Syntax(rfc1903.AutonomousType):
        class Syntax(rfc1903.AutonomousType.Syntax):
            class ObjectSyntax(rfc1902.ObjectSyntax):
                class SimpleSyntax(rfc1902.SimpleSyntax):
                    initialComponent = UsmNoAuthProtocol.ObjectIdentifier
                choiceComponents = [ SimpleSyntax ]
                initialComponent = choiceComponents[0]
            choiceComponents = [ ObjectSyntax ]
            initialComponent = choiceComponents[0]
        fixedComponents = [ Syntax ]
    class Access(rfc1902.ObjectType.Access):
        initialValue = "read-create"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmUser(2).usmUserTable(2).UsmUserEntry(1).usmUserAuthProtocol(5)'
    fixedComponents = [ Syntax, ObjectName ]

class UsmUserCloneFrom(rfc1902.ObjectType):
    class Access(rfc1902.ObjectType.Access):
        initialValue = "read-create"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmUser(2).usmUserTable(2).UsmUserEntry(1).usmUserCloneFrom(4)'
    fixedComponents = [ rfc1903.RowPointer.Syntax, ObjectName ]

class UsmUserSecurityName(rfc1902.ObjectType):
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmUser(2).usmUserTable(2).UsmUserEntry(1).usmUserSecurityName(3)'
    fixedComponents = [ rfc3411.SnmpAdminStringTc.Syntax, ObjectName ]

class UsmUserName(rfc1902.ObjectType):
    class Syntax(rfc3411.SnmpAdminStringTc.Syntax):
        class ObjectSyntax(rfc3411.SnmpAdminStringTc.Syntax.ObjectSyntax):
            class SimpleSyntax(rfc1902.SimpleSyntax):
                class String(rfc1902.OctetString):
                    sizeConstraint = (1, 32)
                    initialValue = 'nobody'
                choiceComponents = [ String ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
    class Access(rfc1902.ObjectType.Access):
        initialValue = "not-accessible"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmUser(2).usmUserTable(2).UsmUserEntry(1).usmUserName(2)'
    fixedComponents = [ Syntax, ObjectName ]

class UsmUserEngineID(rfc1902.ObjectType):
    class Access(rfc1902.ObjectType.Access):
        initialValue = "not-accessible"
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmUser(2).usmUserTable(2).UsmUserEntry(1).usmUserEngineID(1)'
    fixedComponents = [ rfc3411.SnmpEngineIdTc.Syntax, ObjectName ]

class UsmUserEntry(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class TableSyntax(rfc1902.ObjectSyntax.TableSyntax):
                class UsmUserEntryType(rfc1902.Sequence):
                    fixedNames = [ 'usmUserEngineID',
                                   'usmUserName',
                                   'usmUserSecurityName',
                                   'usmUserCloneFrom',
                                   'usmUserAuthProtocol',
                                   'usmUserAuthKeyChange',
                                   'usmUserOwnAuthKeyChange',
                                   'usmUserPrivProtocol',
                                   'usmUserPrivKeyChange',
                                   'usmUserOwnPrivKeyChange',
                                   'usmUserPublic',
                                   'usmUserStorageType',
                                   'usmUserStatus' ]
                    fixedComponents = [ UsmUserEngineID,
                                        UsmUserName,
                                        UsmUserSecurityName,
                                        UsmUserCloneFrom,
                                        UsmUserAuthProtocol,
                                        UsmUserAuthKeyChange,
                                        UsmUserOwnAuthKeyChange,
                                        UsmUserPrivProtocol,
                                        UsmUserPrivKeyChange,
                                        UsmUserOwnPrivKeyChange,
                                        UsmUserPublic,
                                        UsmUserStorageType,
                                        UsmUserStatus ]
                initialComponent = UsmUserEntryType
            initialComponent = TableSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmUser(2).usmUserTable(2).UsmUserEntry(1)'
        initialChildren = [ UsmUserEngineID, UsmUserName,
                            UsmUserSecurityName, UsmUserCloneFrom,
                            UsmUserAuthProtocol, UsmUserAuthKeyChange,
                            UsmUserOwnAuthKeyChange, UsmUserPrivProtocol,
                            UsmUserPrivKeyChange, UsmUserOwnPrivKeyChange,
                            UsmUserPublic, UsmUserStorageType,
                            UsmUserStatus ]

    fixedComponents = [ Syntax, ObjectName ]

class UsmUserTable(rfc1902.ObjectType):
    class Access(rfc1902.ObjectType.Access):
        initialValue = 'not-accessible'
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class TableSyntax(rfc1902.ObjectSyntax.TableSyntax):
                class UsmUserEntries(rfc1902.SequenceOf):
                    protoComponent = UsmUserEntry
                initialComponent = UsmUserEntries
            initialComponent = TableSyntax
        initialComponent = ObjectSyntax
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmUser(2).usmUserTable(2)'
        initialChildren = [ UsmUserEntry ]
    fixedComponents = [ Syntax, ObjectName ]

class UsmUser(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1).usmUser(2)'
    initialChildren = [ UsmUserSpinLock, UsmUserTable ]

class UsmMIBObjects(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBObjects(1)'
    initialChildren = [ UsmStats, UsmUser ]

''' XXX
class UsmMIBCompliance(rfc1902.ModuleCompliance):
    class ObjectIdentifier(rfc1902.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBConformance(2).usmMIBCompliances(1).usmMIBCompliance(1)'
    fixedComponents = [ ObjectIdentifier ]
'''
    
class UsmMIBCompliances(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBConformance(2).usmMIBCompliances(1)'

class UsmMIBGroups(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBConformance(2).usmMIBGroups(2)'

class UsmMIBConformance(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15).usmMIBConformance(2)'
    initialChildren = [ UsmMIBCompliances, UsmMIBGroups ]

class SnmpUsmMIB(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpUsmMIB(15)'
    initialChildren = [ UsmMIBObjects, UsmMIBConformance ]

if __name__ == '__main__':
    from pysnmp.asn1 import oidtree
    import profile
    
    t = oidtree.Root()
    def a():
        t.attachNode(SnmpUsmMIB())
        cell = t.searchNode('.1.3.6.1.6.3.15.1.2.2.1.1')
        print repr(cell)
        newCell = cell.__class__()
        newCell['value'].set('.1.3.6.1.6.3.15.1.2.2.1.1.1')
        t.attachNode(newCell)
#        for i in range(50):
#            t.searchNode('.1.3.6.1.6.3.15.1.2.2.1.1.1')

    profile.run('a()')
#    tbl['table'].append(UsmUserEntry())
#    print repr(tbl)
#    print repr(t.searchNode('.1.3.6.1.6.3.15.1.2.2.1'))    
#    print t.strNode()

