"""
   ASN.1 "universal" data types.

   Written by Ilya Etingof <ilya@glas.net>, 1999-2002.
"""
# Module public names
__all__ = [ 'Boolean', 'Integer', 'BitString', 'OctetString', 'Null', \
            'ObjectIdentifier', 'Real', 'Enumerated', 'Sequence', \
            'SequenceOf', 'Set', 'SetOf' ]

from types import IntType, LongType, StringType, NoneType, FloatType
import string
import asn1, error

#
# ASN.1 "simple" types implementation
#

class Boolean(asn1.SimpleAsn1Object):
    """An ASN.1 boolean object
    """
    tagId = 0x01
    allowedTypes = [ IntType, LongType ]
    singleValueConstraint = [ 0, 1 ]
    initialValue = 0L

    # Disable not applicible constraints
    _subtype_value_range_constraint = asn1.Asn1Object._subtype_value_range_constraint_na
    _subtype_size_constraint = asn1.Asn1Object._subtype_size_constraint_na
    _subtype_permitted_alphabet_constraint = asn1.Asn1Object._subtype_permitted_alphabet_constraint_na

class Integer(asn1.SimpleAsn1Object):
    """An ASN.1, indefinite length integer object
    """
    tagId = 0x02
    allowedTypes = [ IntType, LongType ]
    initialValue = 0L

    # Disable not applicible constraints
    _subtype_size_constraint = asn1.Asn1Object._subtype_size_constraint_na
    _subtype_permitted_alphabet_constraint = asn1.Asn1Object._subtype_permitted_alphabet_constraint_na

class BitString(asn1.SimpleAsn1Object):
    """An ASN.1 BITSTRING object
    """
    tagId = 0x03
    allowedTypes = [ StringType ]

    # Disable not applicible constraints
    _subtype_value_range_constraint = asn1.Asn1Object._subtype_value_range_constraint_na
    _subtype_permitted_alphabet_constraint = asn1.Asn1Object._subtype_permitted_alphabet_constraint_na

class OctetString(asn1.SimpleAsn1Object):
    """ASN.1 octet string object
    """
    tagId = 0x04
    allowedTypes = [ StringType ]

    # Disable not applicible constraints
    _subtype_value_range_constraint = asn1.Asn1Object._subtype_value_range_constraint_na
    _subtype_permitted_alphabet_constraint = asn1.Asn1Object._subtype_permitted_alphabet_constraint_na

class Null(asn1.SimpleAsn1Object):
    """ASN.1 NULL object
    """
    tagId = 0x05
    allowedTypes = [ IntType, LongType, StringType, NoneType ]
    singleValueConstraint = [ 0, 0L, '', None ]

    # Disable not applicible constraints
    _subtype_contained_subtype_constraint = asn1.Asn1Object._subtype_contained_subtype_constraint_na
    _subtype_value_range_constraint = asn1.Asn1Object._subtype_value_range_constraint_na
    _subtype_size_constraint = asn1.Asn1Object._subtype_size_constraint_na
    _subtype_permitted_alphabet_constraint = asn1.Asn1Object._subtype_permitted_alphabet_constraint_na

class ObjectIdentifier(asn1.SimpleAsn1Object):
    """ASN.1 Object ID object (taken and returned as string in conventional
       "dotted" representation)
    """
    tagId = 0x06
    initialValue = []
    allowedTypes = [ StringType ]

    # Disable not applicible constraints
    _subtype_value_range_constraint = asn1.Asn1Object._subtype_value_range_constraint_na
    _subtype_size_constraint = asn1.Asn1Object._subtype_size_constraint_na
    _subtype_permitted_alphabet_constraint = asn1.Asn1Object._subtype_permitted_alphabet_constraint_na
    
    # List like interface
    def __len__(self): return len(self.value)
    def __getitem__(self, i): return self.value[i]
    def __setitem__(self, i, item): self.value[i] = item
    def __delitem__(self, i): del self.value[i]
    def append(self, item): self.value.append(item)

    def isaprefix(self, other):
        """
           isaprefix(other) -> boolean
           
           Compare our own OID with the other one (given as a string),
           return non-None if ours is a prefix of the other OID.

           This is intended to be used for MIB tables retrieval.
        """
        # Pick the shortest oid
        if len(self.value) <= len(other.value):
            # Get the length
            length = len(self.value)

            # Compare oid'es
            if self.value[:length] == other.value[:length]:
                return not None

        # Our OID turned to be greater than the other
        return None

    def str2num(self, soid):
        """
            str2num(soid) -> noid
            
            Convert Object ID "soid" presented in a dotted form into an
            Object ID "noid" represented as a list of numeric sub-ID's.
        """    
        # Convert string into a list and filter out empty members
        # (leading dot causes this)
        try:
            toid = filter(lambda x: len(x), string.split(soid, '.'))

        except:
            raise error.BadArgumentError('Malformed Object ID %s for %s' %\
                                         (str(soid), self.__class__.__name__))

        # Convert a list of symbols into a list of numbers
        try:
            noid = map(lambda x: string.atol(x), toid)

        except:
            raise error.BadArgumentError('Malformed Object ID %s for %s' %\
                                         (str(soid), self.__class__.__name__))

        if not noid:
            raise error.BadArgumentError('Empty Object ID %s for %s' %\
                                         (str(soid), self.__class__.__name__))

        return noid

    def num2str(self, noid):
        """
            num2str(noid) -> snoid
            
            Convert Object ID "noid" presented as a list of numeric
            sub-ID's into Object ID "soid" in dotted notation.
        """    
        if not noid:
            raise error.BadArgumentError('Empty numeric Object ID for %s' %\
                                         self.__class__.__name__)

        # Convert a list of number into a list of symbols and merge all
        # list members into a string
        try:
            soid = reduce(lambda x, y: x+y,\
                          map(lambda x: '.%lu' % x, noid))
        except:
            raise error.BadArgumentError('Malformed numeric Object ID %s for %s' % (str(noid), self.__class__.__name__))
 
        if not soid:
            raise error.BadArgumentError('Empty numeric Object ID %s for %s' %\
                                         (str(noid), self.__class__.__name__))

        return soid

    _iconv = str2num
    _oconv = num2str
            
class Real(asn1.SimpleAsn1Object):
    """An ASN.1 REAL object
    """
    tagId = 0x09
    allowedTypes = [ IntType, LongType, FloatType ]
    initialValue = 0.0

    # Disable not applicible constraints
    _subtype_size_constraint = asn1.Asn1Object._subtype_size_constraint_na
    _subtype_permitted_alphabet_constraint = asn1.Asn1Object._subtype_permitted_alphabet_constraint_na

class Enumerated(asn1.SimpleAsn1Object):
    """An ASN.1 ENUMERATED object
    """
    tagId = 0x10
    allowedTypes = [ IntType, LongType ]
    initialValue = 0

    # Disable not applicible constraints
    _subtype_value_range_constraint = asn1.Asn1Object._subtype_value_range_constraint_na    
    _subtype_size_constraint = asn1.Asn1Object._subtype_size_constraint_na
    _subtype_permitted_alphabet_constraint = asn1.Asn1Object._subtype_permitted_alphabet_constraint_na

#
# ASN.1 "structured" types implementation
#

class Sequence(asn1.StructuredAsn1Object):
    """ASN.1 sequence object
    """
    tagId = 0x10

    # Disable not applicible constraints
    _subtype_size_constraint = asn1.Asn1Object._subtype_size_constraint_na
    _subtype_permitted_alphabet_constraint = asn1.Asn1Object._subtype_permitted_alphabet_constraint_na

class SequenceOf(asn1.StructuredAsn1Object):
    """ASN.1 Sequence Of object
    """
    tagId = 0x10

    # Disable not applicible constraints
    _subtype_permitted_alphabet_constraint = asn1.Asn1Object._subtype_permitted_alphabet_constraint_na

class Set(asn1.StructuredAsn1Object):
    """ASN.1 Set object
    """
    tagId = 0x11

    # Disable not applicible constraints
    _subtype_size_constraint = asn1.Asn1Object._subtype_size_constraint_na
    _subtype_permitted_alphabet_constraint = asn1.Asn1Object._subtype_permitted_alphabet_constraint_na

class SetOf(asn1.StructuredAsn1Object):
    """ASN.1 Set Of object
    """
    tagId = 0x11

    # Disable not applicible constraints
    _subtype_permitted_alphabet_constraint = asn1.Asn1Object._subtype_permitted_alphabet_constraint_na
