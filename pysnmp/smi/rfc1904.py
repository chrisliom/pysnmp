"""
   Conformance Statements for SNMPv2 (RFC1904)

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'ObjectGroup', 'NotificationGroup', 'ModuleCompliance',
            'AgentCapabilities' ]

from pysnmp.proto.rfc1902 import *

class ObjectGroup(Sequence):
    """Definitions for conformance groups (MACRO) XXX
    """
    class ObjectsPart(Choice):
        class Objects(SequenceOf):
            class Object: pass
            protoComponent = Object
        choiceNames = [ 'objects', 'empty' ]
        choiceComponents = [ Objects, Null]
    class Status(OctetString):
        singleValueConstraint = [ "current", "deprecated", "obsolete" ]
        initialValue = singleValueConstraint[0]
    class Description(OctetString): pass
    class ReferPart(Choice):
        class Text(OctetString): pass
        choiceNames = [ 'text', 'empty' ]
        choiceComponents = [ Text, Null ]
    class ObjectIdentifier(ObjectIdentifier): pass
    fixedNames = [ 'object_part', 'value' ]
    fixedComponents = [ ObjectsPart, ObjectIdentifier ]

    def __init__(self, **kwargs):
        """Define and initialize object structure
        """
        # Object properties
        self.objectsPart = self.__class__.ObjectsPart()
        self.status = self.__class__.Status()
        self.description = self.__class__.Description()
        self.referPart = self.__class__.ReferPart()
        apply(Sequence.__init__, [self], kwargs)

    def __str__(self):
        """Returns printable ASN.1 object representation along with
           non-ASN.1 object properties
        """
        return Sequence.__str__(self) + ' %s %s %s %s' % \
               (self.objectsPart, self.status, self.description,
                self.referPart)

class NotificationGroup(Sequence):
    """Mode definitions for conformance groups (MACRO) XXX
    """
    class NotificationsPart(SequenceOf):
        class Notification: pass
        protoComponent = Notification
    class Status(OctetString):
        singleValueConstraint = [ "current", "deprecated", "obsolete" ]
        initialValue = singleValueConstraint[0]
    class Description(OctetString): pass
    class ReferPart(Choice):
        class Text(OctetString): pass
        choiceNames = [ 'text', 'empty' ]
        choiceComponents = [ Text, Null ]
    class ObjectIdentifier(ObjectIdentifier): pass
    fixedNames = [ 'value', 'notifications_part' ]
    fixedComponents = [ ObjectIdentifier, NotificationsPart ]

    def __init__(self, **kwargs):
        """Define and initialize object structure
        """
        # Object properties
        self.notificationsPart = self.__class__.NotificationsPart()
        self.status = self.__class__.Status()
        self.description = self.__class__.Description()
        self.referPart = self.__class__.ReferPart()
        apply(Sequence.__init__, [self], kwargs)

    def __str__(self):
        """Returns printable ASN.1 object representation along with
           non-ASN.1 object properties
        """
        return Sequence.__str__(self) + ' %s %s %s %s' % \
               (self.notificationsPart, self.status, self.description,
                self.referPart)

class ModuleCompliance(Sequence):
    """Definitions for compliance statements (MACRO) XXX
    """
    class Status(OctetString):
        singleValueConstraint = [ "current", "deprecated", "obsolete" ]
        initialValue = singleValueConstraint[0]
    class Description(OctetString): pass
    class ReferPart(Choice):
        class Text(OctetString): pass
        choiceNames = [ 'text', 'empty' ]
        choiceComponents = [ Text, Null ]
    class ModulePart(Choice):
        class Modules(SequenceOf):
            class Module(Sequence):
                class ModuleName(Choice):
                    class ModuleIdentifier(Choice):
                        choiceNames = [ 'value', 'empty' ]
                        choiceComponents = [ ObjectIdentifier, Null ]
                    choiceNames = [ 'id', 'empty' ]
                    choiceComponents = [ ModuleIdentifier, Null ]
                class MandatoryPart(Choice):
                    class Groups(SequenceOf):
                        class Group(ObjectIdentifier): pass
                        protoComponent = Group
                    choiceNames = [ 'groups', 'empty' ]
                    choiceComponents = [ Groups, Null ]                
                class CompliancePart(Choice):
                    class Compliances(SequenceOf):
                        class Compliance(Choice):
                            class ComplianceGroup(Sequence):
                                class Group(ObjectIdentifier): pass
                                class Description(OctetString): pass
                                fixedNames = [ 'group', 'description' ]
                                fixedComponents = [ Group, Description ]
                            class Object(Sequence):
                                class SyntaxPart(Choice):
                                    choiceNames = [ 'syntax', 'empty' ]
                                    choiceComponents = [ ObjectSyntax, Null ]
                                class WriteSyntaxPart(Choice):
                                    choiceNames = [ 'syntax', 'empty' ]
                                    choiceComponents = [ ObjectSyntax, Null ]
                                class AccessPart(Choice):
                                    class Access(OctetString):
                                        singleValueConstraint = [ 'not-accessible', 'accessible-for-notify', 'read-only', 'read-write', 'read-create' ]
                                    choiceNames = [ 'min_access', 'empty' ]
                                    choiceComponents = [ Access, Null ]
                                fixedNames = [ 'object', 'syntax',
                                               'writesyntax' ]
                                fixedComponents = [ ObjectName, SyntaxPart,
                                                    WriteSyntaxPart ]
                                def __init__(self, **kwargs):
                                    self.status = self.__class__.Status()
                                    self.description = self.__class__.Description()
                fixedNames = [ 'name', 'mandatory_part', 'compliance_part' ]
                fixedComponents = [ ModuleName, MandatoryPart, CompliancePart ]
            protoComponent = Module
        choiceNames = [ 'modules', 'empty' ]
        choiceComponents = [ Modules, Null ]
    class ObjectIdentifier(ObjectIdentifier): pass
    fixedNames = [ 'module_part', 'value' ]
    fixedComponents = [ ModulePart, ObjectIdentifier ]

    def __init__(self, **kwargs):
        """Define and initialize object structure
        """
        # Object properties
        self.status = self.__class__.Status()
        self.description = self.__class__.Description()
        self.referPart = self.__class__.ReferPart()
        apply(Sequence.__init__, [self], kwargs)

    def __str__(self):
        """Returns printable ASN.1 object representation along with
           non-ASN.1 object properties
        """
        return Sequence.__str__(self) + ' %s %s %s' % \
               (self.status, self.description, self.referPart)

class AgentCapabilities(Sequence):
    """Definitions for capabilities statements (MACRO) XXX
    """
    class ProductRelease(OctetString): pass
    class Status(OctetString):
        singleValueConstraint = [ "current", "obsolete" ]
        initialValue = singleValueConstraint[0]
    class Description(OctetString): pass
    class ReferPart(Choice):
        class Text(OctetString): pass
        choiceNames = [ 'text', 'empty' ]
        choiceComponents = [ Text, Null ]
    class ModulePart(Choice):
        class Modules(SequenceOf):
            class Module(Sequence):
                class ModuleName(Choice):
                    class ModuleIdentifier(Choice):
                        choiceNames = [ 'value', 'empty' ]
                        choiceComponents = [ ObjectIdentifier, Null ]
                    choiceNames = [ 'id', 'empty' ]
                    choiceComponents = [ ModuleIdentifier, Null ]
                class Groups(SequenceOf):
                    class Group(ObjectIdentifier): pass
                    protoComponent = Group
                class VariationPart(Choice):
                    class Variations(SequenceOf):
                        class Variation(Choice):
                            class ObjectVariation(Sequence):
                                class SyntaxPart(Choice):
                                    choiceNames = [ 'syntax', 'empty' ]
                                    choiceComponents = [ ObjectSyntax, Null ]
                                class WriteSyntaxPart(Choice):
                                    choiceNames = [ 'syntax', 'empty' ]
                                    choiceComponents = [ ObjectSyntax, Null ]
                                class AccessPart(Choice):
                                    class Access(OctetString):
                                        singleValueConstraint = [ 'not-implemented', 'accessible-for-notify' ]
                                    choiceNames = [ 'access', 'empty' ]
                                    choiceComponents = [ Access, Null ]
                                fixedNames = [ 'value', 'syntax',
                                               'writesyntax' ]
                                fixedComponents = [ ObjectName, SyntaxPart,
                                                    WriteSyntaxPart ]
                                class CreationPart(Choice):
                                    class Cells(SequenceOf):
                                        class Cell(Sequence):
                                            fixedNames = [ 'value' ]
                                            fixedComponents = [ ObjectName ]
                                    choiceNames = [ 'cells', 'empty' ]
                                    choiceComponents = [ Cells, Null ]
                                class DefValPart(Choice):
                                    choiceNames = [ 'value', 'empty' ]
                                    choiceComponents = [ ObjectSyntax, Null ]
                                class Description(OctetString): pass
                                def __init__(self, **kwargs):
                                    self.status = self.__class__.Status()
                                    self.accessPart = self.__class__.AccessPart()
                                    self.creationPart = self.__class__.CreationPart()
                                    self.description = self.__class__.Description()
                                    apply(Sequence.__init__, [self], kwargs)
                                fixedNames = [ 'variation', 'syntax',
                                               'write_syntax', 'def_val' ]
                                fixedComponents = [ ObjectName, SyntaxPart,
                                                    WriteSyntaxPart,
                                                    DefValPart ]
                            class NotificationVariation(Sequence):
                                class Description(OctetString): pass
                                class AccessPart(Choice):
                                    class Access(OctetString):
                                        singleValueConstraint = [ 'not-implemented', 'accessible-for-notify' ]
                                    choiceNames = [ 'access', 'empty' ]
                                    choiceComponents = [ Access, Null ]
                                fixedNames = [ 'variation' ]
                                fixedComponents = [ ObjectName ]
                                def __init__(self, **kwargs):
                                    self.accessPart = self.__class__.AccessPart()
                                    self.description = self.__class__.Description()
                                    apply(Sequence.__init__, [self], kwargs)
                                        
                            choiceNames = [ 'object_variation', 'notification_variation' ]
                            choiceComponents = [ ObjectVariation, NotificationVariation ]
                    choiceNames = [ 'variations', 'empty' ]
                    choiceComponents = [ Variations, Null ]
                fixedNames = [ 'name', 'variation_part' ]
                fixedComponents = [ ModuleName, VariationPart ]
            protoComponent = Module
        choiceNames = [ 'modules', 'empty' ]
        choiceComponents = [ Modules, Null ]
    class ObjectIdentifier(ObjectIdentifier): pass
    fixedNames = [ 'module_part', 'value' ]
    fixedComponents = [ ModulePart, ObjectIdentifier ]

    def __init__(self, **kwargs):
        """Define and initialize object structure
        """
        # Object properties
        self.productRelease = self.__class__.ProductRelease()
        self.status = self.__class__.Status()
        self.description = self.__class__.Description()
        self.referPart = self.__class__.ReferPart()
        apply(Sequence.__init__, [self], kwargs)

    def __str__(self):
        """Returns printable ASN.1 object representation along with
           non-ASN.1 object properties
        """
        return Sequence.__str__(self) + ' %s %s %s %s' % \
               (self.productRelease, self.status, self.description,
                self.referPart)
