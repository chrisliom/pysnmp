"""BER codecs for "universal" ASN.1 data types"""
__all__ = [ 'BooleanBerCodec', 'IntegerBerCodec', 'OctetStringBerCodec',
            'BitStringBerCodec', 'NullBerCodec', 'ObjectIdentifierBerCodec',
            'RealBerCodec', 'EnumeratedBerCodec', 'SequenceBerCodec',
            'SequenceOfBerCodec', 'SetBerCodec', 'SetOfBerCodec',
            'ChoiceBerCodec' ]

from string import join
from pysnmp.asn1 import univ
from pysnmp.asn1.encoding.ber import base, error
from pysnmp.asn1.error import Asn1Error

class BooleanBerCodec(base.SimpleBerCodecBase):
    def encodeValue(self, client):        
        if client.rawAsn1Value:
            return '\377'
        else:
            return '\000'

    def decodeValue(self, client, oStream):
        if len(oStream) != 1:
            raise error.BadEncodingError(
                'Wrongly sized input (%d != 1) at %s' %
                (len(oStream), self.__class__.__name__)
            )
        value = ord(oStream[0])
        client.verifyConstraints(value)
        client.rawAsn1Value = value

class IntegerBerCodec(base.SimpleBerCodecBase):
    def encodeValue(self, client):
        oStream = ''
        value = client.rawAsn1Value
    
        # The 0 and -1 values need to be handled separately since
        # they are the terminating cases of the positive and negative
        # cases repectively.
        if value == 0:
            oStream = '\000'
        elif value == -1:
            oStream = '\377'
        elif value < 0:
            while value <> -1:
                value, oStream = value>>8, chr(value & 0xff) + oStream
                
            if ord(oStream[0]) & 0x80 == 0:
                oStream = chr(0xff) + oStream
        else:
            while value > 0:
                value, oStream = value>>8, chr(value & 0xff) + oStream
            if ord(oStream[0]) & 0x80 <> 0:
                oStream = chr(0x00) + oStream
        return oStream
    
    def decodeValue(self, client, oStream):
        bytes = map(ord, oStream)
        if not bytes:
            raise error.BadEncodingError(
                'Empty octet-stream at %s' % self.__class__.__name__
            )        
        if bytes[0] & 0x80:
            bytes.insert(0, -1L)
        value = 0L
        for byte in bytes:
            value = value << 8 | byte
        try:
            value = int(value)
        except OverflowError:
            pass
        client.verifyConstraints(value)
        client.rawAsn1Value = value

class OctetStringBerCodec(base.SimpleBerCodecBase):
    def encodeValue(self, client): return client.rawAsn1Value
    def decodeValue(self, client, oStream):
        client.verifyConstraints(oStream)
        client.rawAsn1Value = oStream

class BitStringBerCodec(OctetStringBerCodec): pass

class NullBerCodec(base.SimpleBerCodecBase):
    def encodeValue(self, client): return ''
    def decodeValue(self, client, oStream):
        if oStream:
            raise error.BadEncodingError(
                'Wrongly sized octet-stream (len(%d) > 0) at %r for %r' %
                (len(oStream), self.__class__.__name__,
                 client.__class__.__name__)
            )

class ObjectIdentifierBerCodec(base.SimpleBerCodecBase):
    def encodeValue(self, client):
        oid = client.rawAsn1Value

        # Make sure the Object ID is long enough
        if len(oid) < 2:
            raise error.BadArgumentError(
                'Short Object ID at %r for %r: %s' %
                (self.__class__.__name__, client.__class__.__name__, oid)
            )

        # Build the first twos
        index = 0
        value = oid[index] * 40
        value = value + oid[index+1]
        if 0 > value > 0xff:
            raise error.BadArgumentError(
                'Initial sub-ID overflow %s at %r for %r' %
                (oid[index:],  self.__class__.__name__,
                 client.__class__.__name__)
            )
        value = [ chr(value) ]
        index = index + 2

        # Cycle through subids
        for subid in oid[index:]:
            if subid > -1 and subid < 128:
                # Optimize for the common case
                value.append(chr(subid & 0x7f))
            elif subid < 0 or subid > 0xFFFFFFFFL:
                raise error.BadArgumentError(
                    'SubId overflow %s at %r for %r' %
                    (subid, self.__class__.__name__,
                     client.__class__.__name__)
                )
            else:
                # Pack large Sub-Object IDs
                res = [ chr(subid & 0x7f) ]
                subid = subid >> 7
                while subid > 0:
                    res.insert(0, chr(0x80 | (subid & 0x7f)))
                    subid = subid >> 7

                # Convert packed Sub-Object ID to string and add packed
                # it to resulted Object ID
                value.append(join(res, ''))

        return join(value, '')
        
    def decodeValue(self, client, oStream):
        oid = []
        index = 0

        if not oStream:
            raise error.BadArgumentError(
                'Short octet-stream (<1) at %r for %r' %
                (self.__class__.__name__, client.__class__.__name__)
            )
        # Get the first subid
        subid = ord(oStream[index])
        oid.append(int(subid / 40))
        oid.append(int(subid % 40))

        index = index + 1
        oStreamLen = len(oStream)
        
        while index < oStreamLen:
            subid = ord(oStream[index])

            if subid < 128:
                oid.append(subid)
                index = index + 1
            else:
                # Construct subid from a number of octets
                next = subid
                subid = 0
                while next >= 128:
                    # Collect subid
                    subid = (subid << 7) + (next & 0x7F)

                    # Take next octet
                    index = index + 1
                    next = ord(oStream[index])

                    # Just for sure
                    if index > len(oStream):
                        raise error.BadArgumentError(
                            'Malformed sub-Object ID at %r for %r' %
                            (self.__class__.__name__,
                             client.__class__.__name__)
                        )

                # Append a subid to oid list
                subid = (subid << 7) + next
                oid.append(subid)
                index = index + 1

        client.verifyConstraints(oid)
        client.rawAsn1Value = tuple(oid)

class RealBerCodec(base.SimpleBerCodecBase): pass
class EnumeratedBerCodec(IntegerBerCodec): pass

# BER for structured ASN.1 objects

codecId = base.codecId

class SequenceBerCodec(base.MappingTypeBerCodecBase):
    def decodeValue(self, client, oStream):
        for key in client.protoSequence:
            oStream = client[key].decodeItem(oStream, codecId)
        return oStream

class SequenceOfBerCodec(base.SequenceTypeBerCodec): pass
class SetBerCodec(base.MappingTypeBerCodecBase):
    def decodeValue(self, client, oStream):
        while oStream:
           for key in client.keys():
               try:
                   oStream = client[key].decodeItem(oStream, codecId)
               except Asn1Error:
                   continue
               break
           else:
               return oStream
           
class SetOfBerCodec(base.SequenceTypeBerCodec): pass

class ChoiceBerCodec(base.MappingTypeBerCodecBase):
    def decodeValue(self, client, oStream):
        # Try current component first
        try:
            if client: return client[client.keys()[0]].decodeItem(oStream, codecId)
        except Asn1Error:
            pass
        # Otherwise, try all components one by one
        for protoName in client.protoComponents.keys():
            component = client.componentFactoryBorrow(protoName)
            try:
                restOfStream = component.decodeItem(oStream, codecId)
            # XXX narrow exception filter
            except Asn1Error, why:
                continue
            client[protoName] = component
            return restOfStream
        else:
            raise error.TypeMismatchError(
                'Octet-stream parse error at %r for %r' %
                (self.__class__.__name__, client.__class__.__name__)
            )    

# Register codecs at their clients
for destClass, codecClass in ( (univ.Boolean, BooleanBerCodec),
                               (univ.Integer, IntegerBerCodec),
                               (univ.BitString, BitStringBerCodec),
                               (univ.OctetString, OctetStringBerCodec),
                               (univ.Null, NullBerCodec),
                               (univ.ObjectIdentifier,
                                ObjectIdentifierBerCodec),
                               (univ.Real, RealBerCodec),
                               (univ.Enumerated, EnumeratedBerCodec),
                               (univ.Sequence, SequenceBerCodec),
                               (univ.SequenceOf, SequenceOfBerCodec),
                               (univ.Set, SetBerCodec),
                               (univ.SetOf, SetOfBerCodec),
                               (univ.Choice, ChoiceBerCodec) ):
    # XXX
    destClass.codecs = {}
    destClass.codecs[codecId] = codecClass()
    destClass.defaultCodec = codecId
