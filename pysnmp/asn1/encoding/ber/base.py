"""Base classes for BER codecs"""
from types import StringType
from string import join
from pysnmp.asn1.base import tagCategories
from pysnmp.asn1.encoding.ber import error

codecId = 'BER'

class AbstractBerCodec:
    # Abstract interface to BER codec

    def encodeValue(self, client):
        """encodeValue(client) -> oStream"""
        raise error.BadArgumentError(
            'No BER value encoder implemented at %r for %r' %
            (self.__class__.__name__, client.__class__.__name__)
        )

    def decodeValue(self, client, oStream):
        """decodeValue(client, oStream) -> restOfStream"""
        raise error.BadArgumentError(
            'No BER value decoder implemented at %r for %r' %
            (self.__class__.__name__, client.__class__.__name__)
        )

    def encode(self, client):
        oStream = self.encodeValue(client)
        if client.tagCategory == tagCategories['IMPLICIT']:
            taggingSequence = (
                client.tagClass[0] | client.tagFormat[0] | client.tagId[0],
            )
        elif client.tagCategory == tagCategories['UNTAGGED']:
            taggingSequence = ()
        elif client.tagCategory == tagCategories['EXPLICIT']:
            return map(lambda x, y, z: x|y|z, client.tagClass, \
                       client.tagFormat, client.tagId)            
        else:
            raise error.BadArgumentError(
                'Unsupported tagCategory (%d) at %s for %s' %
                (client.tagCategory, self.__class__.__name__,
                 client.__class__.__name__,)
            )
        idx = len(taggingSequence)
        while idx:
            idx = idx - 1
            # Encode length
            length = len(oStream)
            if length < 0x80:
                berLength = chr(length)
            elif length < 0xFF:
                berLength = '\x81%c' % length
            elif length < 0xFFFF:
                berLength = '\x82%c%c' % ((length >> 8) & 0xFF, length & 0xFF)
            elif length < 0xFFFFFF:
                berLength = '\x83%c%c%c' % (
                    (length >> 16) & 0xFF,
                    (length >> 8) & 0xFF,
                    length & 0xFF
            )
            # More octets may be added
            else:
                raise error.OverFlowError(
                    'Too large length %d at %r' %
                    (length, self.__class__.__name__)
                )
            oStream = chr(taggingSequence[idx]) + berLength + oStream
        return oStream
    
    def decode(self, client, oStream):
        restOfStream = None
        if client.tagCategory == tagCategories['IMPLICIT']:
            taggingSequence = (
                client.tagClass[0] | client.tagFormat[0] | client.tagId[0],
            )
        elif client.tagCategory == tagCategories['UNTAGGED']:
            taggingSequence = ()
        elif client.tagCategory == tagCategories['EXPLICIT']:
            return map(lambda x, y, z: x|y|z, client.tagClass, \
                       client.tagFormat, client.tagId)            
        else:
            raise error.BadArgumentError(
                'Unsupported tagCategory (%d) at %s for %s' %
                (client.tagCategory, self.__class__.__name__,
                 client.__class__.__name__,)
            )
        for tag in taggingSequence:
            # Decode BER tag
            if len(oStream) < 2:
                raise error.UnderRunError(
                    'Short octet stream (no tag) at %r' %
                    self.__class__.__name__
            )
            gotTag = ord(oStream[0])
            if gotTag != tag:
                raise error.TypeMismatchError(
                    'Tag mismatch at %r for %r: expected %o but got %o' %
                    (self.__class__.__name__, client.__class__.__name__,
                     tag, gotTag)
                )

            # Decode length
            while 1:
                lenOfStream = len(oStream)
                if lenOfStream < 2:
                    raise error.BadEncodingError(
                        'Short octet stream (<2) at %r' %
                        self.__class__.__name__
                    )
                firstOctet  = ord(oStream[1])
                msb = firstOctet & 0x80
                if not msb:
                    length, size = firstOctet & 0x7F, 1
                    break

                if lenOfStream < 3:
                    raise error.BadEncodingError(
                        'Short octet stream (<3) at %r' %
                        self.__class__.__name__
                    )
                size = firstOctet & 0x7F
                secondOctet  = ord(oStream[2])
                if msb and size == 1:
                    length, size = secondOctet, size+1
                    break
            
                if lenOfStream < 4:
                    raise error.BadEncodingError(
                        'Short octet stream (<4) at %r' %
                        self.__class__.__name__
                    )
                if msb and size == 2:
                    length = secondOctet
                    length = length << 8
                    length, size = length | ord(oStream[3]), size+1
                    break

                if lenOfStream < 5:
                    raise error.BadEncodingError(
                        'Short octet stream (<5) at %r' %
                        self.__class__.__name__
                    )
                if msb and size == 3:
                    length = secondOctet
                    length = length << 8
                    length = length | ord(oStream[3])
                    length = length << 8
                    length, size = length | ord(oStream[4]), size+1
                    break

                raise error.OverFlowError(
                    'Too many length bytes %d at %r' %
                    (size, self.__class__.__name__)
                )
            if len(oStream) - 1 - size < length:
                raise error.UnderRunError(
                    'Incomplete octet-stream at %r for %r' %
                    (self.__class__.__name__, client.__class__.__name__)
                )
            if restOfStream is None:
                restOfStream = oStream[1+size+length:]
            oStream = oStream[1+size:1+size+length]
            
        # Untagged item
        if restOfStream is None:
            return self.decodeValue(client, oStream)
        if self.decodeValue(client, oStream):
            raise error.TypeMismatchError(
                'Extra data left in wire at %r for %r: %s' %
                (self.__class__.__name__, client.__class__.__name__,
                 repr(oStream))
            )
        return restOfStream

class SimpleBerCodecBase(AbstractBerCodec): pass
class StructuredBerCodecBase(AbstractBerCodec): pass

class MappingTypeBerCodecBase(StructuredBerCodecBase):
    def encodeValue(self, client):
        oStream = []
        for key in client.keys():
            oStream.append(client[key].encodeItem(codecId))            
        return join(oStream, '')

class SequenceTypeBerCodec(StructuredBerCodecBase):
    def encodeValue(self, client):
        oStream = []
        for component in client:
            oStream.append(component.encodeItem(codecId))
        return join(oStream, '')

    def decodeValue(self, client, oStream):
        client.clear()
        while oStream:
            protoComponent = client.componentFactoryBorrow()
            oStream = protoComponent.decodeItem(oStream, codecId)
            client.append(protoComponent)
