"""
   Managed Object Definitions for SNMP Management Frameworks (RFC3411)

   Written by Ilya Etingof <ilya@glas.net>, 2002.
"""
from pysnmp.smi import rfc1902, rfc1903

class SnmpEngineIdTc(rfc1903.TextualConvention):
    class Syntax(rfc1903.TextualConvention.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class SimpleSyntax(rfc1902.SimpleSyntax):
                class String(rfc1902.OctetString):
                    sizeConstraint = (5, 32)
                    initialValue = '12345'
                choiceComponents = [ String ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class SnmpSecurityModelTc(rfc1903.TextualConvention):
    class Syntax(rfc1903.TextualConvention.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class SimpleSyntax(rfc1902.SimpleSyntax):
                class Integer(rfc1902.Integer):
                    valueRangeConstraint = (0, 2147483647)
                    initialValue = 3                    
                choiceComponents = [ Integer ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class SnmpMessageProcessingModelTc(rfc1903.TextualConvention):
    class Syntax(rfc1903.TextualConvention.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class SimpleSyntax(rfc1902.SimpleSyntax):
                class Integer(rfc1902.Integer):
                    valueRangeConstraint = (0, 2147483647)
                    initialValue = 3                    
                choiceComponents = [ Integer ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class SnmpSecurityLevelTc(rfc1903.TextualConvention):
    class Syntax(rfc1903.TextualConvention.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class SimpleSyntax(rfc1902.SimpleSyntax):
                class Integer(rfc1902.Integer):
                    singleValueConstraint = [1, 2, 3]
                    initialValue = 1                    
                choiceComponents = [ Integer ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class SnmpAdminStringTc(rfc1903.TextualConvention):
    class DisplayPart(rfc1903.TextualConvention.DisplayPart):
        class Text(rfc1902.OctetString):
            initialValue = "255a"
        choiceComponents = [ Text, rfc1902.Null ]
        initialComponent = Text    
    class Syntax(rfc1903.TextualConvention.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class SimpleSyntax(rfc1902.SimpleSyntax):
                class String(rfc1902.OctetString):
                    sizeConstraint = (0, 255)
                choiceComponents = [ String ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class SnmpEngineId(rfc1902.ObjectType):
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10).snmpFrameworkMIBObjects(2).snmpEngine(1).snmpEngineID(1)'
    fixedComponents = [ SnmpEngineIdTc.Syntax, ObjectName ]
    
class SnmpEngineBoots(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class SimpleSyntax(rfc1902.SimpleSyntax):
                class Value(rfc1902.Integer):
                    valueRangeConstraint = (1, 2147483647)
                    initialValue = 1
                choiceComponents = [ Value ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10).snmpFrameworkMIBObjects(2).snmpEngine(1).snmpEngineBoots(2)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpEngineTime(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class SimpleSyntax(rfc1902.SimpleSyntax):
                class Value(rfc1902.Integer):
                    valueRangeConstraint = (0, 2147483647)
                    initialValue = 0
                choiceComponents = [ Value ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]

    class UnitsPart(rfc1902.ObjectType.UnitsPart):
        class Units(rfc1902.ObjectType.UnitsPart.Units):
            initialValue = 'seconds'
        initialComponent = Units
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10).snmpFrameworkMIBObjects(2).snmpEngine(1).snmpEngineTime(3)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpEngineMaxMessageSize(rfc1902.ObjectType):
    class Syntax(rfc1902.ObjectType.Syntax):
        class ObjectSyntax(rfc1902.ObjectSyntax):
            class SimpleSyntax(rfc1902.SimpleSyntax):
                class Value(rfc1902.Integer):
                    valueRangeConstraint = (484, 2147483647)
                    initialValue = 65050
                choiceComponents = [ Value ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
    class ObjectName(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10).snmpFrameworkMIBObjects(2).snmpEngine(1).snmpEngineMaxMessageSize(4)'
    fixedComponents = [ Syntax, ObjectName ]

class SnmpEngine(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10).snmpFrameworkMIBObjects(2).snmpEngine(1)'
    initialChildren = [ SnmpEngineId, SnmpEngineBoots, SnmpEngineTime,
                        SnmpEngineMaxMessageSize ]

''' XXX
class SnmpFrameworkMIBCompliance(rfc1902.ModuleCompliance):
    class ObjectIdentifier(rfc1902.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10).snmpFrameworkMIBConformance(3).snmpFrameworkMIBCompliances(1).snmpFrameworkMIBCompliance(1)'
    fixedComponents = [ ObjectIdentifier ]
'''

class SnmpFrameworkMibCompliances(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10).snmpFrameworkMIBConformance(3).snmpFrameworkMIBCompliances(1)'
#    initialChildren = [ SnmpFrameworkMIBCompliance ]
    initialChildren = [ ]
    
class SnmpFrameworkMibGroups(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10).snmpFrameworkMIBConformance(3).snmpFrameworkMIBGroups(2)'

class SnmpFrameworkMibConformance(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10).snmpFrameworkMIBConformance(3)'
    initialChildren = [ SnmpFrameworkMibCompliances,
                        SnmpFrameworkMibGroups ]

class SnmpFrameworkMibObjects(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10).snmpFrameworkMIBObjects(2)'
    initialChildren = [ SnmpEngine ]

# Registration Points for Authentication and Privacy Protocols

class SnmpAuthProtocols(rfc1902.ObjectIdentity):
    class ObjectIdentifier(rfc1902.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10).snmpFrameworkAdmin(1).snmpAuthProtocols(1)'
    fixedComponents = [ ObjectIdentifier ]

class SnmpPrivProtocols(rfc1902.ObjectIdentity):
    class ObjectIdentifier(rfc1902.ObjectIdentifier):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10).snmpFrameworkAdmin(1).snmpPrivProtocols(2)'
    fixedComponents = [ ObjectIdentifier ]

class SnmpFrameworkAdmin(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10).snmpFrameworkAdmin(1)'
    initialChildren = [ SnmpAuthProtocols ]

class SnmpFrameworkMib(rfc1902.ModuleIdentity):
    class LastUpdated(rfc1902.ModuleIdentity.LastUpdated):
        initialValue = "9901190000Z"
    class Organization(rfc1902.ModuleIdentity.Organization):
        initialValue = "SNMPv3 Working Group"
    class RevisionPart(rfc1902.ModuleIdentity.RevisionPart):
        class Revisions(rfc1902.ModuleIdentity.RevisionPart.Revisions):
            class Revision(rfc1902.ModuleIdentity.RevisionPart.Revisions.Revision):
                initialValue = "9711200000Z"
        initialComponent = Revisions

    class ObjectIdentifier(rfc1902.ObjectName):
        initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3).snmpFrameworkMIB(10)'
        initialChildren = [ SnmpFrameworkAdmin, \
                            SnmpFrameworkMibObjects, \
                            SnmpFrameworkMibConformance ]
    fixedComponents = [ ObjectIdentifier ]

class SnmpModules(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6).snmpModules(3)'
    initialChildren = [ SnmpFrameworkMib ]
    
class SnmpV2(rfc1902.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6)'
    initialChildren = [ SnmpModules ]

if __name__ == '__main__':

    from pysnmp.asn1 import oidtree

    t = oidtree.Root()
#    t.attachNode(SnmpEngineId()['value'], SnmpEngineId())
    t.attachNode(SnmpV2())
    print t.strNode()
    print str(SnmpEngineBoots())
#    t.getNode('.iso(1).3.6.1.6.3.10.2.1.1')['type']['type']['simple_syntax']['string'].set('kukuku')
#    print repr(t.getNode('.iso(1).3.6.1.6.3.10.2.1.1')['type']['type']['simple_syntax']['string'].get())    

