"""Abstract interface class to various serializers"""
from pysnmp.asn1 import univ
from pysnmp.asn1.encoding import error

# Some code is dup'ed inline here for performance reasons
    
class CodecDecorator:
    # Codecs registry
    codecs = {}
    defaultCodec = None
    
    def encodeItem(self, codecId=None):
        if codecId is None:
            codecId = self.defaultCodec
        codec = self.codecs.get(codecId)
        if codec is None:
            raise error.BadArgumentError(
                'Unsupported codec \'%s\' at %s' %
                (codecId, self.__class__.__name__)
            )
        return codec.encode(self)

    def decodeItem(self, octetStream, codecId=None):
        if codecId is None:
            codecId = self.defaultCodec
        codec = self.codecs.get(codecId)
        if codec is None:
            raise error.BadArgumentError(
                'Unsupported codec \'%s\' at %s' %
                (codecId, self.__class__.__name__)
            )
        return codec.decode(self, octetStream)

    # XXX
    encode = berEncode = encodeItem
    decode = berDecode = decodeItem

class CachingCodecDecorator(CodecDecorator):
    # Cache encoded values. Applicible to immutable types only.
    def encodeItem(self, codecId=None):
        if codecId is None:
            codecId = self.defaultCodec

        # Hash object (not __hash__ for performance reasons)
        newHash = hash((self.rawAsn1Value, self.tagClass, self.tagFormat,
                        self.tagId, self.tagCategory))
        
        # Cache lookup
        encoderCache = getattr(self, '_encoderCache', None)
        if encoderCache is None:
            self._encoderCache = { codecId: None }
        else:
            avPair = encoderCache.get(codecId, None)
            if avPair is not None:
                cachedHash, oStream = avPair
                if newHash == cachedHash:
                    return oStream

        # Codec lookup
        codec = self.codecs.get(codecId)
        if codec is None:
            raise error.BadArgumentError(
                'Unsupported codec \'%s\' at %s' %
                (codecId, self.__class__.__name__)
            )

        # Encode and cache
        oStream = codec.encode(self)
        self._encoderCache[codecId] = (newHash, oStream) # Cache update
        return oStream

    # XXX
    encode = berEncode = encodeItem
    
# Mix-in codec interface classes into ASN.1 type classes
for baseClass, mixInClass in ( (univ.Boolean, CachingCodecDecorator),
                               (univ.Integer, CachingCodecDecorator),
                               (univ.BitString, CachingCodecDecorator),
                               (univ.OctetString, CachingCodecDecorator),
                               (univ.Null, CachingCodecDecorator),
                               (univ.ObjectIdentifier, CachingCodecDecorator),
                               (univ.Real, CachingCodecDecorator),
                               (univ.Enumerated, CachingCodecDecorator),
                               (univ.Sequence, CodecDecorator),
                               (univ.SequenceOf, CodecDecorator),
                               (univ.Set, CodecDecorator),
                               (univ.SetOf, CodecDecorator),
                               (univ.Choice, CodecDecorator) ):
    if mixInClass not in baseClass.__bases__:
        baseClass.__bases__ = baseClass.__bases__ + (mixInClass, )
