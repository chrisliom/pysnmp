"""
   Textual Conventions for SNMPv2 (RFC1903)

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'TextualConvention', 'DisplayString', 'PhysAddress',
            'MacAddress', 'TruthValue', 'TestAndIncr', 'AutonomousType',
            'InstancePointer', 'VariablePointer', 'RowPointer',
            'RowStatus', 'TimeStamp', 'TimeInterval', 'DateAndTime',
            'StorageType', 'TDomain', 'TAddress' ]

from pysnmp.proto.rfc1902 import *

class TextualConvention(Sequence):
    class DisplayPart(Choice):
        class Text(OctetString): pass
        choiceNames = [ 'text', 'empty' ];
        choiceComponents = [ Text, Null ]
        initialComponent = Null

    class Status(OctetString):
        singleValueConstraint = [ "current", "deprecated", "obsolete" ]
        initialValue = singleValueConstraint[0]

    class Description(OctetString):
        initialValue = "N/A"

    class ReferPart(Choice):
        class Reference(OctetString): pass
        choiceNames = [ 'text', 'empty' ];
        choiceComponents = [ Reference, Null ]
    
    class Syntax(Choice):
        class Kibbles(SequenceOf):
            class Kibble(Sequence):
                fixedNames = [ 'identifier' ];
                fixedComponents = [ Unsigned32 ]
        choiceNames = [ 'type', 'bits' ]
        choiceComponents = [ ObjectSyntax, Kibbles ]

    fixedNames = ['type' ]
    fixedComponents = [ Syntax ]

    def __init__(self, **kwargs):
        """Define and initialize object structure
        """
        # Object properties
        self.displayPart = self.__class__.DisplayPart()
        self.status = self.__class__.Status()
        self.description = self.__class__.Description()
        self.referPart = self.__class__.ReferPart()

        apply(Sequence.__init__, [self], kwargs)

    def __str__(self):
        """Returns printable ASN.1 object representation along with
           non-ASN.1 object properties
        """
        return Sequence.__str__(self) + ' %s %s %s %s' % \
               (self.displayPart, self.status, self.description,
                self.referPart)

class DisplayString(TextualConvention):
    class DisplayPart(TextualConvention.DisplayPart):
        class Text(OctetString):
            initialValue = "255a"
        choiceComponents = [ Text, Null ]
        initialComponent = Text
    class Status(TextualConvention.Status):
        initialValue = "current"
    class Description(TextualConvention.Description):
        initialValue = "N/A"
    class Syntax(TextualConvention.Syntax):
        class ObjectSyntax(ObjectSyntax):
            class SimpleSyntax(SimpleSyntax):
                class String(OctetString):
                    sizeConstraint = (0, 255)
                choiceComponents = [ String ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class PhysAddress(TextualConvention):
    class DisplayPart(TextualConvention.DisplayPart):
        class Text(OctetString):
            initialValue = "1x:"
        choiceComponents = [ Text, Null ]
        initialComponent = Text
    class Status(TextualConvention.Status):
        initialValue = "current"
    class Description(TextualConvention.Description):
        initialValue = "N/A"
    class Syntax(TextualConvention.Syntax):
        class ObjectSyntax(ObjectSyntax):
            class SimpleSyntax(SimpleSyntax):
                class String(OctetString): pass
                choiceComponents = [ String ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class MacAddress(TextualConvention):
    class DisplayPart(TextualConvention.DisplayPart):
        class Text(OctetString):
            initialValue = "1x:"
        choiceComponents = [ Text, Null ]
        initialComponent = Text
    class Status(TextualConvention.Status):
        initialValue = "current"
    class Description(TextualConvention.Description):
        initialValue = "N/A"
    class Syntax(TextualConvention.Syntax):
        class ObjectSyntax(ObjectSyntax):
            class SimpleSyntax(SimpleSyntax):
                class String(OctetString):
                    sizeConstraint = (6, 6)
                choiceComponents = [ String ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class TruthValue(TextualConvention):
    class Status(TextualConvention.Status):
        initialValue = "current"
    class Description(TextualConvention.Description):
        initialValue = "N/A"
    class Syntax(TextualConvention.Syntax):
        class ObjectSyntax(ObjectSyntax):
            class SimpleSyntax(SimpleSyntax):
                class Integer(Integer):
                    singleValueConstraint = [1, 2]
                    initialValue = 1
                choiceComponents = [ Integer ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class TestAndIncr(TextualConvention):
    class Status(TextualConvention.Status):
        initialValue = "current"
    class Description(TextualConvention.Description):
        initialValue = "N/A"
    class Syntax(TextualConvention.Syntax):
        class ObjectSyntax(ObjectSyntax):
            class SimpleSyntax(SimpleSyntax):
                class Integer(Integer):
                    valueRangeConstraint = (0, 2147483647)
                choiceComponents = [ Integer ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class AutonomousType(TextualConvention):
    class Status(TextualConvention.Status):
        initialValue = "current"
    class Description(TextualConvention.Description):
        initialValue = "N/A"
    class Syntax(TextualConvention.Syntax):
        class ObjectSyntax(ObjectSyntax):
            class SimpleSyntax(SimpleSyntax):
                choiceComponents = [ ObjectIdentifier ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class InstancePointer(TextualConvention):
    class Status(TextualConvention.Status):
        initialValue = "obsolete"
    class Description(TextualConvention.Description):
        initialValue = "N/A"
    class Syntax(TextualConvention.Syntax):
        class ObjectSyntax(ObjectSyntax):
            class SimpleSyntax(SimpleSyntax):
                choiceComponents = [ ObjectIdentifier ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class VariablePointer(TextualConvention):
    class Status(TextualConvention.Status):
        initialValue = "current"
    class Description(TextualConvention.Description):
        initialValue = "N/A"
    class Syntax(TextualConvention.Syntax):
        class ObjectSyntax(ObjectSyntax):
            class SimpleSyntax(SimpleSyntax):
                choiceComponents = [ ObjectIdentifier ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class RowPointer(TextualConvention):
    class Status(TextualConvention.Status):
        initialValue = "current"
    class Description(TextualConvention.Description):
        initialValue = "N/A"
    class Syntax(TextualConvention.Syntax):
        class ObjectSyntax(ObjectSyntax):
            class SimpleSyntax(SimpleSyntax):
                choiceComponents = [ ObjectIdentifier ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class RowStatus(TextualConvention):
    class Status(TextualConvention.Status):
        initialValue = "current"
    class Description(TextualConvention.Description):
        initialValue = "N/A"
    class Syntax(TextualConvention.Syntax):
        class ObjectSyntax(ObjectSyntax):
            class SimpleSyntax(SimpleSyntax):
                class Integer(Integer):
                    singleValueConstraint = [1, 2, 3, 4, 5, 6 ]
                    initialValue = 1
                choiceComponents = [ Integer ]
                initialComponent = choiceComponents[0]
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class TimeStamp(TextualConvention):
    class Status(TextualConvention.Status):
        initialValue = "current"
    class Description(TextualConvention.Description):
        initialValue = "N/A"
    class Syntax(TextualConvention.Syntax):
        class ObjectSyntax(ObjectSyntax):
            class SimpleSyntax(SimpleSyntax):
                choiceComponents = [ TimeTicks ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class TimeInterval(TextualConvention):
    class Status(TextualConvention.Status):
        initialValue = "current"
    class Description(TextualConvention.Description):
        initialValue = "N/A"
    class Syntax(TextualConvention.Syntax):
        class ObjectSyntax(ObjectSyntax):
            class SimpleSyntax(SimpleSyntax):
                class Integer(Integer):
                    valueRangeConstraint = (0, 2147483647)
                choiceComponents = [ Integer ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class DateAndTime(TextualConvention):
    class DisplayPart(TextualConvention.DisplayPart):
        class Text(OctetString):
            initialValue = "2d-1d-1d,1d:1d:1d.1d,1a1d:1d"
        choiceComponents = [ Text, Null ]
        initialComponent = Text
    class Status(TextualConvention.Status):
        initialValue = "current"
    class Description(TextualConvention.Description):
        initialValue = "N/A"
    class Syntax(TextualConvention.Syntax):
        class ObjectSyntax(ObjectSyntax):
            class SimpleSyntax(SimpleSyntax):
                class String(OctetString):
                    sizeConstraint = (8, 11)
                choiceComponents = [ String ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class StorageType(TextualConvention):
    class Status(TextualConvention.Status):
        initialValue = "current"
    class Description(TextualConvention.Description):
        initialValue = "N/A"
    class Syntax(TextualConvention.Syntax):
        class ObjectSyntax(ObjectSyntax):
            class SimpleSyntax(SimpleSyntax):
                class Integer(Integer):
                    singleValueConstraint = [1, 2, 3, 4, 5 ]
                    initialValue = 1
                choiceComponents = [ Integer ]
                initialComponent = choiceComponents[0]
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class TDomain(TextualConvention):
    class Status(TextualConvention.Status):
        initialValue = "current"
    class Description(TextualConvention.Description):
        initialValue = "N/A"
    class Syntax(TextualConvention.Syntax):
        class ObjectSyntax(ObjectSyntax):
            class SimpleSyntax(SimpleSyntax):
                choiceComponents = [ ObjectIdentifier ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]

class TAddress(TextualConvention):
    class Status(TextualConvention.Status):
        initialValue = "current"
    class Description(TextualConvention.Description):
        initialValue = "N/A"
    class Syntax(TextualConvention.Syntax):
        class ObjectSyntax(ObjectSyntax):
            class SimpleSyntax(SimpleSyntax):
                class String(OctetString):
                    sizeConstraint = (1, 255)
                choiceComponents = [ String ]
                initialComponent = choiceComponents[0]                
            choiceComponents = [ SimpleSyntax ]
            initialComponent = choiceComponents[0]
        choiceComponents = [ ObjectSyntax ]
        initialComponent = choiceComponents[0]
        
    fixedComponents = [ Syntax ]
