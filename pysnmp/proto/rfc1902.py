"""Implementation of data types defined by SNMP SMI (RFC1902)"""
from pysnmp.proto import rfc1155, error
from pysnmp.asn1 import univ, tags, subtypes

__all__ = [
    'Integer', 'Integer32', 'OctetString', 'BitString', 'Null', \
    'ObjectIdentifier', 'IpAddress', 'Counter32', 'Gauge32', \
    'Unsigned32', 'TimeTicks', 'Opaque',  'Counter64', 'Sequence', \
    'Bits', 'SequenceOf', 'Choice', 'ObjectName', 'SimpleSyntax', \
    'ApplicationSyntax', 'ObjectSyntax'
    ]

# SimpleSyntax

class Integer(univ.Integer):
    # Subtyping -- value range constraint
    subtypeConstraints = (
        subtypes.ValueRangeConstraint(-2147483648L, 2147483647L),
    )

class Integer32(univ.Integer):
    # Subtyping -- value range constraint
    subtypeConstraints = (
        subtypes.ValueRangeConstraint(-2147483648L, 2147483647L),
    )
    
class BitString(univ.BitString): pass

class OctetString(univ.OctetString):
    # Subtyping -- size constraint    
    subtypeConstraints = ( subtypes.ValueSizeConstraint(0, 65535), )

Null = univ.Null
ObjectIdentifier = univ.ObjectIdentifier

# ApplicationSyntax

class IpAddress(rfc1155.IpAddressInterfaceMixIn, univ.OctetString):
    tagSet = univ.OctetString.tagSet.clone(
        tagClass=tags.tagClassApplication, tagId=0x00
        )
    # Subtyping -- size constraint
    subtypeConstraints = ( subtypes.ValueSizeConstraint(4, 4), )
    initialValue = '\000\000\000\000'

class Counter32(univ.Integer):
    tagSet = univ.Integer.tagSet.clone(
        tagClass=tags.tagClassApplication, tagId=0x01
        )
    # Subtyping -- value range constraint
    subtypeConstraints = ( subtypes.ValueRangeConstraint(0, 4294967295L), )

class Gauge32(univ.Integer):
    tagSet = univ.Integer.tagSet.clone(
        tagClass=tags.tagClassApplication, tagId=0x02
        )
    # Subtyping -- value range constraint
    subtypeConstraints = ( subtypes.ValueRangeConstraint(0, 4294967295L), )

class Unsigned32(univ.Integer):
    tagSet = univ.Integer.tagSet.clone(
        tagClass=tags.tagClassApplication, tagId=0x02
        )
    # Subtyping -- value range constraint
    subtypeConstraints = ( subtypes.ValueRangeConstraint(0, 4294967295L), )

class TimeTicks(univ.Integer):
    tagSet = univ.Integer.tagSet.clone(
        tagClass=tags.tagClassApplication, tagId=0x03
        )
    # Subtyping -- value range constraint
    subtypeConstraints = ( subtypes.ValueRangeConstraint(0, 4294967295L), )

class Opaque(univ.OctetString):
    tagSet = univ.OctetString.tagSet.clone(
        tagClass=tags.tagClassApplication, tagId=0x04
        )

class Counter64(univ.Integer):
    tagSet = univ.Integer.tagSet.clone(
        tagClass=tags.tagClassApplication, tagId=0x06
        )
    # Subtyping -- value range constraint
    subtypeConstraints = (
        subtypes.ValueRangeConstraint(0, 18446744073709551615L),
    )

# XXX ?
class Bits(OctetString): pass
Sequence = univ.Sequence
SequenceOf = univ.SequenceOf
Choice = univ.Choice

class ObjectName(ObjectIdentifier): pass

class SimpleSyntax(univ.Choice):
    protoComponents = { 'integer_value': Integer(),
                        'string_value': OctetString(),
                        'objectID_value': ObjectIdentifier(),
                        'bit_value': BitString() }

class ApplicationSyntax(univ.Choice):
    protoComponents = { 'ipAddress_value': IpAddress(),
                        'counter_value': Counter32(),
                        'timeticks_value': TimeTicks(),
                        'arbitrary_value': Opaque(),
                        'big_counter_value': Counter64(),
                        'unsigned_integer_value': Unsigned32(),
                        'gauge32_value': Gauge32(),
                        'bits_value': Bits() } # BITS misplaced?

class ObjectSyntax(univ.Choice):
    class TableSyntax(univ.Choice):
        protoComponents = { 'table': SequenceOf(),
                            'row': Sequence() }
    protoComponents = { 'simple_syntax': SimpleSyntax(),
                        'application_syntax': ApplicationSyntax(),
                        'sequence_syntax': TableSyntax() }
