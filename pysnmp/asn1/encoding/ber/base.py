"""
   A framework for implementing Basic Encoding Rules (BER) en/decoders
   for ASN.1 data types.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'SimpleAsn1Object', 'OrderedFixedTypeAsn1Object', \
            'UnorderedFixedTypeAsn1Object', 'SingleFixedTypeAsn1Object', \
            'OrderedVariableTypeAsn1Object', 'UnorderedVariableTypeAsn1Object']

from types import StringType
from string import join
from pysnmp.asn1.encoding.ber import error
from pysnmp.asn1.base import tagCategories

def decodeTag(input, where='decodeTag'):
    """Decode first octet of input octet stream into int tag
    """
    if type(input) != StringType:
        raise error.BadArgumentError('Non-string type input %s at %s' %\
                                     (type(input), where))
    if len(input) < 2:
        raise error.UnderRunError('Short octet stream (no tag) at %s' % where)
    
    return ord(input[0])

class BerObject:
    """Base class for BER en/decoding classes
    """
    # A placeholders for ASN.1-defined attributes XXX
    tagClass = tagFormat = tagId = 0
    
    def berEncodeTag(self, (tagClass, tagFormat, tagId) = (None, None, None)):
        """BER encode ASN.1 type tag
        """
        if tagClass is None:
            tagClass = self.tagClass
        if tagFormat is None:
            tagFormat = self.tagFormat
        if tagId is None:
            tagId = self.tagId

        return chr(tagClass | tagFormat | tagId)

    def berEncodeLength(self, length):
        """
           berEncodeLength(length) -> octet string
           
           BER encode ASN.1 data item length (integer).
        """
        # If given length fits one byte
        if length < 0x80:
            # Pack it into one octet
            return chr(length)
        
        # One extra byte required
        elif length < 0xFF:
            # Pack it into two octets
            return join(map(chr, [0x81, length]), '')
        
        # Two extra bytes required
        elif length < 0xFFFF:
            # Pack it into three octets
            return join(map(chr, [0x82, (length >> 8) & 0xFF,
                                  length & 0xFF]), '')
        
        # Three extra bytes required
        elif length < 0xFFFFFF:
            # Pack it into three octets
            return join(map(chr, [0x83, (length >> 16) & 0xFF,
                                  (length >> 8) & 0xFF, length & 0xFF]), '')
        
        # More octets may be added
        else:
            raise error.OverFlowError('Too large length %d for %s' %\
                                      (length, self.__class__.__name__))

    def berDecodeLength(self, input):
        """
           berDecodeLength(input) -> (length, size)
           
           Return the data item's length (integer) and the size of length
           data (integer).
        """
        if len(input) < 1:
            raise error.BadEncodingError('Short octet stream at %s' %\
                                         self.__class__.__name__)

        # Get the most-significant-bit
        msb = ord(input[0]) & 0x80
        if not msb:
            return (ord(input[0]) & 0x7F, 1)

        if len(input) < 2:
            raise error.BadEncodingError('Short octet stream at %s' %\
                                         self.__class__.__name__)
        
        # Get the size if the length
        size = ord(input[0]) & 0x7F

        # One extra byte length
        if msb and size == 1:
            return (ord(input[1]), size+1)

        if len(input) < 3:
            raise error.BadEncodingError('Short octet stream at %s' %\
                                         self.__class__.__name__)
        
        # Two extra bytes length
        if msb and size == 2:
            result = ord(input[1])
            result = result << 8
            return (result | ord(input[2]), size+1)

        if len(input) < 4:
            raise error.BadEncodingError('Short octet stream at %s' %\
                                         self.__class__.__name__)

        # Two extra bytes length
        if msb and size == 3:
                result = ord(input[1])
                result = result << 8
                result = result | ord(input[2])
                result = result << 8
                return (result | ord(input[3]), size+1)

        raise error.OverFlowError('Too many length bytes %d for %s' %\
                                  (size, self.__class__.__name__))

class SimpleAsn1Object(BerObject):
    """BER packet header encoders & decoders for simple (that is non-structured
       ASN.1 objects)
    """
    def berEncode(self, value=None):
        """
            berEncode() -> octet string
            
            BER encode object payload whenever possible
        """
        if not hasattr(self, '_berEncode'):
            raise error.BadArgumentError('No encoder defined for %s' %\
                                         self.__class__.__name__)
        
        if value is not None and hasattr(self, 'set'):
            self.set(value); value = self.rawAsn1Value
        if value is None and hasattr(self, 'rawAsn1Value'):
            value = self.rawAsn1Value

        if self.tagCategory == tagCategories['EXPLICIT']:
            for superClass in self.__class__.__bases__:
                if issubclass(superClass, SimpleAsn1Object):
                    break
            else:
                raise error.BadArgumentError('No underling type for %s' % \
                                             self.__class__.__name__)
            
            if value is None:
                value = superClass.berEncodeTag(self, self.getUnderlyingTag())\
                        + superClass.berEncodeLength(self, 0)
            else:
                value = superClass._berEncode(self, value)
                value = superClass.berEncodeTag(self, self.getUnderlyingTag())\
                        + superClass.berEncodeLength(self, len(value)) + result

        if value is None:
            return self.berEncodeTag() + self.berEncodeLength(0)
        else:
            value = self._berEncode(value)
            return self.berEncodeTag() + \
                   self.berEncodeLength(len(value)) + value

    encode = berEncode
    
    def berDecode(self, input):
        """
            berDecode(input) -> (value, rest)
            
            BER decode input (octet string) into ASN1 object payload,
            return the rest of input stream.
        """
        if not hasattr(self, '_berDecode'):
            raise error.BadArgumentError('No decoder defined for %s' %\
                                         self.__class__.__name__)

        if decodeTag(input, self.__class__.__name__) != \
           self.tagClass | self.tagFormat | self.tagId:
            raise error.TypeMismatchError('Tag mismatch %o at %s' %\
                                          (decodeTag(input), \
                                           self.__class__.__name__))
        
        (length, size) = self.berDecodeLength(input[1:])
        if len(input) - 1 - size < length:
            raise error.UnderRunError('Short input for %s' %\
                                      self.__class__.__name__)

        value = self._berDecode(input[1+size:1+size+length])

        if hasattr(self, '_setRawAsn1Value'):
            self._setRawAsn1Value(value)

        return input[1+size+length:]
    
    decode = berDecode
    
class StructuredAsn1Object(SimpleAsn1Object):
    """BER for structured ASN.1 objects
    """
    def berWrapHeader(self, input):
        """Add BER header to data chunk if needed
        """
        if self.tagCategory == tagCategories['UNTAGGED']:
            return input
        else:
            return self.berEncodeTag() + \
                   self.berEncodeLength(len(input)) + input

    def berUnwrapHeader(self, input):
        """Decode BER header, return (data, rest)
        """
        if self.tagCategory == tagCategories['UNTAGGED']:
            return (input, '')
        else:
            if decodeTag(input, self.__class__.__name__) != \
               self.tagClass | self.tagFormat | self.tagId:
                raise error.TypeMismatchError('Tag mismatch %o at %s' %\
                                              (decodeTag(input), \
                                               self.__class__.__name__))
        
            (length, size) = self.berDecodeLength(input[1:])
            if len(input) - 1 - size < length:
                raise error.UnderRunError('Short input for %s' % \
                                          self.__class__.__name__)

            return (input[1+size:1+size+length], input[1+size+length:])

class FixedTypeAsn1Object(StructuredAsn1Object):
    """BER for fixed-type ASN.1 objects
    """
    def berEncode(self, **kwargs):
        """
            berEncode() -> octet string
            
            BER encode object payload whenever possible
        """
        self.update(kwargs)

        if hasattr(self, '_berEncode'):
            result = self._berEncode()
        else:
            result = ''
            for key in self.keys():
                result = result + self[key].encode()

        return self.berWrapHeader(result)
    
    encode = berEncode
    
class OrderedFixedTypeAsn1Object(FixedTypeAsn1Object):
    """BER for ordered, fixed-type ASN.1 objects
    """
    def berDecode(self, input):
        """
            berDecode(input) -> rest
            
            BER decode input (octet string) into ASN1 object payload,
            return the rest of input stream.
        """
        (input, rest) = self.berUnwrapHeader(input)
        
        if hasattr(self, '_berDecode'):
            input = self._berDecode(input)
        else:
            for key in self.keys():
                input = self[key].berDecode(input)

        if len(rest):
            return rest
        else:
            return input

    decode = berDecode
    
class UnorderedFixedTypeAsn1Object(FixedTypeAsn1Object):
    """BER for unordered, fixed-type ASN.1 objects
    """
    def berDecode(self, input):
        """
            berDecode(input) -> rest
            
            BER decode input (octet string) into ASN1 object payload,
            return the rest of input stream.
        """
        (input, rest) = self.berUnwrapHeader(input)
            
        if hasattr(self, '_berDecode'):
            input = self._berDecode(input)
        else:
            keys = self.keys()
            while keys:
                for key in keys:
                    try:
                        input = self[key].berDecode(input)

                    except error.TypeMismatchError:
                        continue

                    keys.remove(key)
                    break
                else:
                    raise error.TypeMismatchError('Unregistered tag %o at %s'\
                                                  % (decodeTag(input), \
                                                     self.__class__.__name__))
        if len(rest):
            return rest
        else:
            return input

    decode = berDecode
    
class SingleFixedTypeAsn1Object(FixedTypeAsn1Object):
    """BER for a single, fixed-type ASN.1 objects
    """
    def berDecode(self, input):
        """
            berDecode(input) -> rest
            
            BER decode input (octet string) into ASN1 object payload,
            return the rest of input stream.
        """
        (input, rest) = self.berUnwrapHeader(input)            
        if hasattr(self, '_berDecode'):
            input = self._berDecode(input)
        else:
            # XXX improve input[:1] based caching
            if not hasattr(self, '_cachedChoiceComponents'):
                self._cachedChoiceComponents = {}            
            while 1:
                # First try current component
                if len(self):
                    try:
                        input = self.values()[0].berDecode(input)
                    except error.TypeMismatchError:
                        pass
                    else:
                        break
                # Secondly, try cache
                cachedValues = self._cachedChoiceComponents.get(input[:1], None)
                if cachedValues is not None:
                    for (name, value) in cachedValues:
                        try:
                            input = value.berDecode(input)
                        except error.TypeMismatchError:
                            continue
                        else:
                            self[name] = value
                            break
                else:
                    # At last, try all components one by one
                    cachedValues = self._cachedChoiceComponents.get(input[:1], None)
                    if cachedValues is None:
                        self._cachedChoiceComponents[input[:1]] = cachedValues = []
                    idx = 0
                    for idx in range(len(self.choiceComponents)):
                        for (name, value) in cachedValues:
                            if isinstance(value, self.choiceComponents[idx]):
                                break
                        else:
                            name, value = (self.choiceNames[idx], \
                                           self.choiceComponents[idx]())
                            cachedValues.append((name, value))
                        try:
                            input = value.berDecode(input)
                        except error.TypeMismatchError:
                            continue
                        else:
                            self[name] = value
                            break
                    else:
                        raise error.TypeMismatchError('Unregistered tag %o at %s' %\
                                                      (decodeTag(input), \
                                                       self.__class__.__name__))
                break

        if len(rest):
            return rest
        else:
            return input

    decode = berDecode
    
class VariableTypeAsn1Object(StructuredAsn1Object):
    """BER for variable-type ASN.1 objects
    """
    def berEncode(self, args=[]):
        """
            berEncode() -> octet string
            
            BER encode object payload whenever possible
        """
        self.extend(args)

        if hasattr(self, '_berEncode'):
            result = self._berEncode()
        else:
            result = ''
            for value in self:
                result = result + value.berEncode()

        return self.berWrapHeader(result)

    encode = berEncode

    def berDecode(self, input):
        """
            berDecode(input) -> rest
            
            BER decode input (octet string) into ASN1 object payload,
            return the rest of input stream.
        """
        (input, rest) = self.berUnwrapHeader(input)

        if hasattr(self, '_berDecode'):
            return self._berDecode(input)
        else:
            if not hasattr(self, '_cachedComponents'):
                self._cachedComponents = []
            idx = 0
            while len(input):
                if len(self._cachedComponents) <= idx:
                    self._cachedComponents.append(self.protoComponent())
                input = self._cachedComponents[idx].berDecode(input)
                idx = idx + 1
            self[:] = self._cachedComponents[:idx]
        return rest

    decode = berDecode
    
class OrderedVariableTypeAsn1Object(VariableTypeAsn1Object):
    """BER for ordered, variable-type ASN.1 objects
    """
    pass

class UnorderedVariableTypeAsn1Object(VariableTypeAsn1Object):
    """BER for unordered, variable-type ASN.1 objects
    """
    pass
