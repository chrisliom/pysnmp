"""
   Implementation of data types defined by SNMP SMI (RFC1902)

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'Integer', 'Integer32', 'OctetString', 'Null', \
            'ObjectIdentifier', 'IpAddress', 'Counter32', 'Gauge32', \
            'Unsigned32', 'TimeTicks', 'Opaque',  'Counter64', 'Sequence', \
            'SequenceOf', 'Choice', 'ObjectName', 'SimpleSyntax', \
            'ApplicationSyntax', 'ObjectSyntax' ]

from pysnmp.proto import rfc1155, error
from pysnmp.asn1.base import tagCategories

# SimpleSyntax

class Integer(rfc1155.Integer):
    """SMI INTEGER data type
    """
    # Subtyping -- value range constraint
    valueRangeConstraint = (-2147483648L, 2147483647L)

class Integer32(Integer):
    """SMI INTEGER32 data type
    """
    pass

class OctetString(rfc1155.OctetString):
    """SMI OCTETSTRING data type
    """
    # Subtyping -- size constraint    
    sizeConstraint = (0, 65535)

class Null(rfc1155.Null):
    """SMI NULL data type
    """
    pass

class ObjectIdentifier(rfc1155.ObjectIdentifier):
    """SMI OBJECTIDENTIFIER data type
    """
    pass

# ApplicationSyntax

class IpAddress(rfc1155.IpAddress):
    """SMI IPADDRESS data type
    """
    pass

class Counter32(rfc1155.Counter):
    """SNMP Counter32 object
    """
    pass

class Gauge32(rfc1155.Gauge):
    """SNMP Gauge object
    """
    pass

class Unsigned32(Gauge32):
    """SMI Unsigned32 data type
    """
    pass

class TimeTicks(rfc1155.TimeTicks):
    """SMI TimeTicks object
    """
    pass

class Opaque(rfc1155.Opaque):
    """SMI Opaque object
    """
    # RFC1905 says Opaque is now IMPLICITly tagged %-/
    tagCategory = tagCategories['IMPLICIT']

class Counter64(rfc1155.Counter):
    """SMI Counter64 object
    """
    # Implicit tagging
    tagId = 0x06

    # Subtyping -- value range constraint
    valueRangeConstraint = (0, 18446744073709551615L)

class Sequence(rfc1155.Sequence):
    """SNMP Sequence
    """
    pass

class SequenceOf(rfc1155.SequenceOf):
    """SNMP SequenceOf
    """
    pass

class Choice(rfc1155.Choice):
    """ASN.1 CHOICE clause
    """
    pass

class ObjectName(ObjectIdentifier):
    """Names of objects in MIB
    """
    pass

class SimpleSyntax(Choice):
    """Simple (non-constructed) objects
    """
    choiceNames = [ 'integer_value', 'string_value', 'objectID_value' ]
    choiceComponents = [ Integer, OctetString, ObjectIdentifier ]

class ApplicationSyntax(Choice):
    """Constructed objects
    """
    choiceNames = [ 'ipAddress_value', 'counter_value', 'timeticks_value', \
                    'arbitrary_value', 'big_counter_value', \
                    'unsigned_integer_value', 'unsigned_integer_value' ]

    choiceComponents = [ IpAddress, Counter32, TimeTicks, Opaque, \
                         Counter64, Unsigned32, Gauge32 ]

class ObjectSyntax(Choice):
    """Syntax of objects in MIB
    """
    class TableSyntax(Choice):
        choiceNames = [ 'table', 'row' ]
        choiceComponents = [ SequenceOf, Sequence ]
    choiceNames = [ 'simple_syntax', 'sequence_syntax', 'application_syntax' ]
    choiceComponents = [ SimpleSyntax, TableSyntax, ApplicationSyntax ]
