"""
   SMI-related types as defined by SNMP v2c SMI (RFC1902)

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'SnmpModules', 'SnmpProxys', 'SnmpDomains', 'SnmpV2',
            'Security', 'Enterprises', 'Private', 'Experimental',
            'Transmission', 'Mib2', 'Mgmt', 'Directory',
            'ModuleIdentity', 'ObjectIdentity', 'ObjectType' ]

from pysnmp.proto.rfc1902 import *

class SnmpModules(ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(1).snmpModules(3)'

class SnmpProxys(ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(1).snmpProxys(2)'

class SnmpDomains(ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(1).snmpDomains(1)'

class SnmpV2(ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).snmpV2(6)'
    initialChildren = [ SnmpDomains, SnmpProxys ]

class Security(ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).security(5)'

class Enterprises(ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).private(4).enterprises(1)'

class Private(ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).private(4)'
    initialChildren = [ Enterprises ]

class Experimental(ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).experimental(3)'

class Transmission(ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1).transmission(10)'

class Mib2(ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2).mib-2(1)'
    initialChildren = [ Transmission ]
    
class Mgmt(ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1).mgmt(2)'
    initialChildren = [ Mib2 ]

class Directory(ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1).directory(1)'
    initialChildren = [ Mgmt ]

class ModuleIdentity(Sequence):
    """Module identity definition for MIB objects (normally done by MACRO)
    """
    class LastUpdated(OctetString):
        sizeConstraint = (11, 13)
        initialValue = '00000000000'
    class Organization(OctetString):
        initialValue = "N/A"
    class ContactInfo(OctetString):
        initialValue = "N/A"
    class Description(OctetString):
        initialValue = "N/A"
    class RevisionPart(Choice):
        class Revisions(SequenceOf):
            class Revision(OctetString): sizeConstraint = (10, 11)
            protoComponent = Revision
        choiceNames = [ 'revisions', 'empty' ]
        choiceComponents = [ Revisions, Null ]

    fixedNames = [ 'value' ]
    fixedComponents = [ ObjectIdentifier ]

    def __init__(self, **kwargs):
        """Define and initialize object structure
        """
        # Object properties
        self.lastUpdated = self.__class__.LastUpdated()
        self.organization = self.__class__.Organization()
        self.contactInfo = self.__class__.ContactInfo()
        self.description = self.__class__.Description()
        self.revisionPart = self.__class__.RevisionPart()
        
        apply(Sequence.__init__, [self], kwargs)

    def __str__(self):
        """Returns printable ASN.1 object representation along with
           non-ASN.1 object properties
        """
        return Sequence.__str__(self) + ' %s %s %s %s %s' % \
               (self.lastUpdated, self.organization, \
                self.contactInfo, self.description, self.revisionPart)

    def getKeyOid(self): return self['value']
    
class ObjectIdentity(Sequence):
    """Object identity definition for MIB objects (normally done by MACRO)
    """
    class Status(OctetString):
        singleValueConstraint = [ "current", "deprecated", "obsolete" ]
        initialValue = singleValueConstraint[0]
    class Description(OctetString):
        initialValue = "N/A"
    class ReferPart(Choice):
        class Text(OctetString): pass
        choiceNames = [ 'text', 'empty' ]
        choiceComponents = [ Text, Null ]
       
    fixedNames = [ 'value' ]
    fixedComponents = [ ObjectIdentifier ]

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

    def getKeyOid(self): return self['value']

class ObjectName(ObjectIdentifier): pass

class ObjectType(Sequence):
    """Object type definition for MIB objects (normally done by MACRO)
    """
    class Syntax(Choice):
        class Kibbles(SequenceOf):
            class Kibble(Sequence):
                fixedNames = [ 'identifier' ];
                fixedComponents = [ Unsigned32 ]
        choiceNames = [ 'type', 'bits' ]
        choiceComponents = [ ObjectSyntax, Kibbles ]
    class UnitsPart(Choice):
        class Units(OctetString): pass
        choiceNames = [ 'text', 'empty' ];
        choiceComponents = [ Units, Null ]
        initialComponent = Null
    class Access(OctetString):
        singleValueConstraint = [ "not-accessible", "accessible-for-notify",\
                                  "read-only", "read-write", "read-create" ]
        initialValue = singleValueConstraint[2]
    class Status(OctetString):
        singleValueConstraint = [ "current", "deprecated", "obsolete" ]
        initialValue = singleValueConstraint[0]
    class ReferPart(Choice):
        class Reference(OctetString): pass
        fixedNames = [ 'text', 'empty' ];
        fixedComponents = [ Reference, Null ]
    class IndexPart(Choice):
        class IndexTypes(SequenceOf):
            class Index(Sequence):
                fixedNames = [ 'indexobject' ];
                fixedComponents = [ ObjectName ]
            protoComponent = Index
        class Entry(Sequence):
            fixedNames = [ 'entryobject' ];
            fixedComponents = [ ObjectName ]
        choiceNames = [ 'index', 'augments', 'empty' ]
        choiceComponents = [ IndexTypes, Entry ]

    class Description(OctetString):
        initialValue = "N/A"

# XXX
#    class DefValPart(Choice):
#        choiceNames = [ 'value', 'empty' ];
#        choiceComponents = [ Syntax, Null ]
        
    fixedNames = ['type', 'value' ]
    fixedComponents = [ Syntax, ObjectName ]

    def __init__(self, **kwargs):
        """Define and initialize object structure
        """
        # Object properties
        self.unitsPart = self.__class__.UnitsPart()
        self.access = self.__class__.Access()
        self.status = self.__class__.Status()
        self.referPart = self.__class__.ReferPart()
        self.indexPart = self.__class__.IndexPart()
        self.description = self.__class__.Description()

        apply(Sequence.__init__, [self], kwargs)

    def __str__(self):
        """Returns printable ASN.1 object representation along with
           non-ASN.1 object properties
        """
        return Sequence.__str__(self) + ' %s %s %s %s %s %s' % \
               (self.unitsPart, self.access, self.status, \
                self.referPart, self.indexPart, self.description)

    def getKeyOid(self): return self['value']

class NotificationName(ObjectIdentifier):
    """Names of objects in MIB
    """
    pass

class NotificationType(Sequence):
    """Definitions for notifications
    """
    class ObjectsPart(Choice):
        class Objects(SequenceOf):
            protoComponent = ObjectName
        choiceNames = [ 'objects', 'empty' ]
        choiceComponents = [ Objects, Null]
    class Status(OctetString):
        singleValueConstraint = [ "current", "deprecated", "obsolete" ]
        initialValue = singleValueConstraint[0]
    class ReferPart(Choice):
        class Reference(OctetString): pass
        fixedNames = [ 'text', 'empty' ];
        fixedComponents = [ Reference, Null ]
    class Description(OctetString):
        initialValue = "N/A"

    fixedNames = [ 'type', 'value' ]
    fixedComponents = [ ObjectsPart, NotificationName ]

    def __init__(self, **kwargs):
        """Define and initialize object structure
        """
        # Object properties
        self.status = self.__class__.Status()
        self.referPart = self.__class__.ReferPart()
        self.description = self.__class__.Description()

        apply(Sequence.__init__, [self], kwargs)

    def __str__(self):
        """Returns printable ASN.1 object representation along with
           non-ASN.1 object properties
        """
        return Sequence.__str__(self) + ' %s %s %s' % \
               (self.status, self.referPart, self.description)

    def getKeyOid(self): return self['value']
