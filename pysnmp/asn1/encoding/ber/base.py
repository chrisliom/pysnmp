"""Base classes for BER codecs"""
from types import StringType
from string import join
from pysnmp.asn1.encoding.ber import error

codecId = 'BER'

class AbstractBerCodec:
    # Abstract interface to BER codec

    def encodeValue(self, client):
        """encodeValue(client) -> oStream"""
        raise error.BadArgumentError(
            'No BER value encoder implemented at %s for %s' %
            (self.__class__.__name__, client.__class__.__name__)
        )

    def decodeValue(self, client, oStream):
        """decodeValue(client, oStream) -> restOfStream"""
        raise error.BadArgumentError(
            'No BER value decoder implemented at %s for %s' %
            (self.__class__.__name__, client.__class__.__name__)
        )

    def encode(self, client):
        oStream = self.encodeValue(client)
        for tag in client.tagSet.getTaggingSequence():
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
                    'Too large length %d at %s' %
                    (length, self.__class__.__name__)
                )
            oStream = chr(tag) + berLength + oStream
        return oStream
    
    def decode(self, client, oStream):
        ### all this should be pre-calculated!
        restOfStream = None
        for tag in client.tagSet.getTaggingSequence():
            tag = chr(tag)
            # Decode BER tag
            if len(oStream) < 2:
                raise error.UnderRunError(
                    'Short octet stream (no tag) at %s' %
                    self.__class__.__name__
            )
            # use strings here instead of ord
            gotTag = oStream[0]
            if gotTag != tag:
                raise error.TypeMismatchError(
                    'Tag mismatch at %s for %s: expected %o but got %o' %
                    (self.__class__.__name__, client.__class__.__name__,
                     ord(tag), ord(gotTag))
                )

            ## Hopefully faster length decoding...
            lenOfStream = len(oStream)
            # we know there's at least 2 bytes from above
            firstOctet  = ord(oStream[1])
            if firstOctet < 128:
                length, size = firstOctet, 1
            else:
                size = (firstOctet & 0x7F)
                # encoded in size bytes
                length = 0
                lengthString = oStream[2:size+2]
                # missing check on maximum size, which shouldn't be a problem,
                # we can handle more than is possible
                if len(lengthString) != size:
                    raise error.BadEncodingError(
                        'Expected %s bytes of length encoding for %s, but not enough data in stream, only %s bytes' %
                        size,
                        self.__class__.__name__,
                        len( lengthString ),
                    )
                for char in lengthString:
                    length = (length << 8) | ord(char)
                size = size + 1

            if lenOfStream - 1 - size < length:
                raise error.UnderRunError(
                    'Incomplete octet-stream at %s for %s' %
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
                'Extra data left in wire at %s for %s: %s' %
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
