"""
   SMI-related types as defined by SNMP v1 SMI (RFC1155)

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'ObjectType' ]

from pysnmp.proto.rfc1155 import *

class ObjectType(Sequence):
    """Object type definition for MIB objects (normally done by MACRO)
    """
    class Access(OctetString):
        singleValueConstraint = [ "read-only", "read-write", \
                                  "write-only", "not-accessible"]
        initialValue = singleValueConstraint[0]
        
    class Status(OctetString):
        singleValueConstraint = [ "optional", "obsolete" ]
        initialValue = singleValueConstraint[0]
        
    fixedNames = ['type', 'value']
    fixedComponents = [ ObjectSyntax, ObjectName ]

    def __init__(self, **kwargs):
        """Define and initialize object structure
        """
        # Object properties
        self.access = ObjectType.Access()
        self.status = ObjectType.Status()

        apply(Sequence.__init__, [self], kwargs)

    def __str__(self):
        """Returns printable ASN.1 object representation along with
           non-ASN.1 object properties
        """
        return Sequence.__str__(self) + ' ' + str(self.access) +\
               ' ' + str(self.status)
