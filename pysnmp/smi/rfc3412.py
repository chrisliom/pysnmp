"""
   The MIB for Message Processing and Dispatching (RFC3412)

   Written by Ilya Etingof <ilya@glas.net>, 2002.
"""
from pysnmp.smi import rfc1902, rfc1903, rfc1904

class SnmpMpdAdmin(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMPDMIB(11).snmpMPDAdmin(1)'

class SnmpUnknownSecurityModels(rfc1902.ObjectType):
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
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMPDMIB(11).snmpMPDMIBObjects(2).snmpMPDStats(1).snmpUnknownSecurityModels(1)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpInvalidMsgs(rfc1902.ObjectType):
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
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMPDMIB(11).snmpMPDMIBObjects(2).snmpMPDStats(1).snmpInvalidMsgs(2)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpUnknownPduHandlers(rfc1902.ObjectType):
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
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMPDMIB(11).snmpMPDMIBObjects(2).snmpMPDStats(1).snmpUnknownPDUHandlers(3)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpMpdStats(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMPDMIB(11).snmpMPDMIBObjects(2).snmpMPDStats(1)'
    initialChildren = [ SnmpUnknownSecurityModels, SnmpInvalidMsgs,
                        SnmpUnknownPduHandlers ]

class SnmpMpdMibObjects(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMPDMIB(11).snmpMPDMIBObjects(2)'
    initialChildren = [ SnmpMpdStats ]

class SnmpMpdMib(rfc1902.ModuleIdentity):
    class LastUpdated(rfc1902.ModuleIdentity.LastUpdated):
        initialValue = "9905041636Z"
    class Organization(rfc1902.ModuleIdentity.Organization):
        initialValue = "SNMPv3 Working Group"
    class RevisionPart(rfc1902.ModuleIdentity.RevisionPart):
        class Revisions(rfc1902.ModuleIdentity.RevisionPart.Revisions):
            class Revision1(rfc1902.ModuleIdentity.RevisionPart.Revisions.Revision): initialValue = "9905041636Z"
            class Revision2(rfc1902.ModuleIdentity.RevisionPart.Revisions.Revision): initialValue = "9709300000Z"
            initialValue = [ Revision1, Revision2 ]
        initialComponent = Revisions
    class ObjectIdentifier(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMPDMIB(11)'
        initialChildren = [ SnmpMpdAdmin, SnmpMpdMibObjects ]
    fixedComponents = [ ObjectIdentifier ]

class SnmpMpdGroup(rfc1904.ObjectGroup):
    class ObjectsPart(rfc1904.ObjectGroup.ObjectsPart):
        initialValue = [ SnmpUnknownSecurityModels,
                         SnmpInvalidMsgs,
                         SnmpUnknownPduHandlers ]
    class ObjectIdentifier(rfc1904.ObjectGroup.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMPDMIB(11).snmpMPDMIBConformance(3).snmpMPDMIBGroups(2).snmpMPDGroup(1)'
    fixedComponents = [ ObjectsPart, ObjectIdentifier ]
    
class SnmpMpdCompliance(rfc1904.ModuleCompliance):
    class ModulePart(rfc1904.ModuleCompliance.ModulePart):
        class Modules(rfc1904.ModuleCompliance.ModulePart.Modules):
            class Module(rfc1904.ModuleCompliance.ModulePart.Modules.Module):
                class ModuleName(rfc1904.ModuleCompliance.ModulePart.Modules.Module.ModuleName):
                    class ModuleIdentifier(rfc1904.ModuleCompliance.ModulePart.Modules.Module.ModuleName.ModuleIdentifier):
                        initialComponent = SnmpMpdMib.ObjectIdentifier
                    initialComponent = ModuleIdentifier
                class MandatoryPart(rfc1904.ModuleCompliance.ModulePart.Modules.Module.MandatoryPart):
                    class Groups(rfc1904.ModuleCompliance.ModulePart.Modules.Module.MandatoryPart.Groups):
                        initialValue = [ SnmpMpdGroup.ObjectIdentifier ]
                    initialComponent = Groups
                fixedComponents = [ ModuleName, MandatoryPart, rfc1904.ModuleCompliance.ModulePart.Modules.Module.CompliancePart ]
            initialValue = Module
        initialComponent = Modules
        
    class ObjectIdentifier(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMPDMIB(11).snmpMPDMIBConformance(3).snmpMPDMIBCompliances(1).snmpMPDCompliance(1)'
    fixedComponents = [ ModulePart, ObjectIdentifier ]
        
class SnmpMpdMibCompliances(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMPDMIB(11).snmpMPDMIBConformance(3).snmpMPDMIBCompliances(1)'
    initialChildren = [ SnmpMpdCompliance ]

class SnmpMpdMibGroups(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMPDMIB(11).snmpMPDMIBConformance(3).snmpMPDMIBGroups(2)'
    initialChildren = [ SnmpMpdGroup ]
    
class SnmpMpdMibConformance(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpMPDMIB(11).snmpMPDMIBConformance(3)'
    initialChildren = [ SnmpMpdMibCompliances, SnmpMpdMibGroups ]

if __name__ == '__main__':
    
    from pysnmp.asn1 import oidtree

    t = oidtree.Root()
    t.attachNode(SnmpMpdStats())
    t.attachNode(SnmpMpdMibObjects())
    t.attachNode(SnmpMpdMibConformance())
    print t.searchNode('iso.org.dod.internet.snmpV2.snmpModules.11.3.2.1')
    print repr(t.searchNode('1.3.6.1.6.3.11.2.1.3'))
#    print t.strNode()
