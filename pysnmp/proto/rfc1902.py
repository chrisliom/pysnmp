"""Implementation of data types defined by SNMP SMI (RFC1902)"""

__all__ = [ 'Integer', 'Integer32', 'OctetString', 'BitString', 'Null', \
            'ObjectIdentifier', 'IpAddress', 'Counter32', 'Gauge32', \
            'Unsigned32', 'TimeTicks', 'Opaque',  'Counter64', 'Sequence', \
            'Bits', 'SequenceOf', 'Choice', 'ObjectName', 'SimpleSyntax', \
            'ApplicationSyntax', 'ObjectSyntax' ]

from pysnmp.proto import rfc1155, error
from pysnmp.asn1.base import tagCategories
from pysnmp.asn1 import univ, subtypes

# SimpleSyntax

class Integer(rfc1155.Integer):
    # Subtyping -- value range constraint
    subtypeConstraints = (
        subtypes.ValueRangeConstraint(-2147483648L, 2147483647L),
    )

class Integer32(Integer): pass
class BitString(univ.BitString): pass

class OctetString(rfc1155.OctetString):
    # Subtyping -- size constraint    
    subtypeConstraints = ( subtypes.ValueSizeConstraint(0, 65535), )

class Null(rfc1155.Null): pass
class ObjectIdentifier(rfc1155.ObjectIdentifier): pass

# ApplicationSyntax

class IpAddress(rfc1155.IpAddress): pass
class Counter32(rfc1155.Counter): pass
class Gauge32(rfc1155.Gauge): pass
class Unsigned32(Gauge32): pass
class TimeTicks(rfc1155.TimeTicks): pass
class Opaque(rfc1155.Opaque): pass

class Counter64(rfc1155.Counter):
    tagId = (0x06, )

    # Subtyping -- value range constraint
    subtypeConstraints = (
        subtypes.ValueRangeConstraint(0, 18446744073709551615L),
    )

class Bits(OctetString): pass
class Sequence(rfc1155.Sequence): pass
class SequenceOf(rfc1155.SequenceOf): pass
class Choice(rfc1155.Choice): pass
class ObjectName(ObjectIdentifier): pass

class SimpleSyntax(Choice):
    protoComponents = { 'integer_value': Integer(),
                        'string_value': OctetString(),
                        'objectID_value': ObjectIdentifier(),
                        'bit_value': BitString() }

class ApplicationSyntax(Choice):
    protoComponents = { 'ipAddress_value': IpAddress(),
                        'counter_value': Counter32(),
                        'timeticks_value': TimeTicks(),
                        'arbitrary_value': Opaque(),
                        'big_counter_value': Counter64(),
                        'unsigned_integer_value': Unsigned32(),
                        'gauge32_value': Gauge32(),
                        'bits_value': Bits() } # BITS misplaced?

class ObjectSyntax(Choice):
    class TableSyntax(Choice):
        protoComponents = { 'table': SequenceOf(),
                            'row': Sequence() }
    protoComponents = { 'simple_syntax': SimpleSyntax(),
                        'application_syntax': ApplicationSyntax(),
                        'sequence_syntax': TableSyntax() }
