"""Implementation of data types defined by SNMP SMI (RFC1155, RFC1212)"""

__all__ = [ 'Integer', 'OctetString', 'Null', 'ObjectIdentifier', \
            'IpAddress', 'Counter', 'Gauge', 'TimeTicks', 'Opaque', \
            'Sequence', 'SequenceOf', 'Choice', 'NetworkAddress', \
            'ObjectName', 'SimpleSyntax', 'ApplicationSyntax', \
            'ObjectSyntax']

from string import split, atoi, atoi_error
from types import StringType
from pysnmp.asn1.base import tagClasses
from pysnmp.asn1 import univ, subtypes
import pysnmp.asn1.encoding.ber
from pysnmp.proto import error

# SimpleSyntax

class Integer(univ.Integer): pass
class OctetString(univ.OctetString): pass
class Null(univ.Null): pass
class ObjectIdentifier(univ.ObjectIdentifier): pass

# ApplicationSyntax

class IpAddress(univ.OctetString):
    tagClass = (tagClasses['APPLICATION'], )
    tagId = (0x00, )

    # Subtyping -- size constraint
    subtypeConstraints = ( subtypes.ValueSizeConstraint(4, 4), )
    initialValue = '\000\000\000\000'
    
    def _iconv(self, value):
        # Convert IP address given in dotted notation into an unsigned
        # int value
        try:
            packed = split(value, '.')

        except:
            raise error.BadArgumentError(
                'Malformed IP address %s for %s' %
                (str(value), self.__class__.__name__)
            )
        
        # Make sure it is four octets length
        if len(packed) != 4:
            raise error.BadArgumentError(
                'Malformed IP address %s for %s' %
                (str(value), self.__class__.__name__)
            )

        # Convert string octets into integer counterparts
        try:
            return reduce(lambda x, y: x+y, \
                          map(lambda x: chr(atoi(x)), packed))

        except atoi_error:
            raise error.BadArgumentError(
                'Malformed IP address %s for %s' %
                (str(value), self.__class__.__name__)
            )

    def _oconv(self, value):
        if value:
            # Convert unsigned int value into IP address dotted representation
            return '%d.%d.%d.%d' % (ord(value[0]), ord(value[1]), \
                                    ord(value[2]), ord(value[3]))
        else: return value

class Counter(univ.Integer):
    tagClass = (tagClasses['APPLICATION'], )
    tagId = (0x01, )

    # Subtyping -- value range constraint
    subtypeConstraints = ( subtypes.ValueRangeConstraint(0, 4294967295L), )

class Gauge(univ.Integer):
    tagClass = (tagClasses['APPLICATION'], )
    tagId = (0x02, )

    # Subtyping -- value range constraint
    subtypeConstraints = ( subtypes.ValueRangeConstraint(0, 4294967295L), )

class TimeTicks(univ.Integer):
    tagClass = (tagClasses['APPLICATION'], )
    tagId = (0x03, )

    # Subtyping -- value range constraint
    subtypeConstraints = ( subtypes.ValueRangeConstraint(0, 4294967295L), )

class Opaque(univ.OctetString):
    tagClass = (tagClasses['APPLICATION'], )
    tagId = (0x04, )

class Sequence(univ.Sequence): pass
class SequenceOf(univ.SequenceOf): pass
class Choice(univ.Choice): pass

class NetworkAddress(Choice):
    protoComponents = { 'internet': IpAddress() }

    # Initialize to Internet address
    initialComponentKey = 'internet'

class ObjectName(ObjectIdentifier): pass

class SimpleSyntax(Choice):
    protoComponents = { 'number': Integer(),
                        'string': OctetString(),
                        'object': ObjectIdentifier(),
                        'empty': Null() }
    initialComponentKey = 'empty'

class ApplicationSyntax(Choice):
    protoComponents = { 'address': NetworkAddress(),
                        'counter': Counter(),
                        'gauge': Gauge(),
                        'ticks': TimeTicks(),
                        'arbitrary': Opaque() }

class ObjectSyntax(Choice):
    class TableSyntax(Choice):
        protoComponents = { 'table': SequenceOf(),
                            'row': Sequence() }
    protoComponents = { 'simple': SimpleSyntax(),
                        'application_wide': ApplicationSyntax(),
                        'sequence': TableSyntax() }
    initialComponentKey = 'simple'
