"""ASN.1 "universal" data types"""
import string
from string import join, split, atoi, atol
from operator import getslice
from types import IntType, LongType, StringType, NoneType, FloatType,  \
     TupleType, ListType, SliceType
from exceptions import StandardError, TypeError
from pysnmp.asn1 import base, tags, subtypes, namedval, error

__all__ = [
    'Boolean', 'Integer', 'BitString', 'OctetString', 'Null', 
    'ObjectIdentifier', 'Real', 'Enumerated', 'Sequence',
    'SequenceOf', 'Set', 'SetOf', 'Choice'
    ]

#
# "Simple" ASN.1 types implementation
#

class Boolean(base.AbstractSimpleAsn1Item):
    tagSet = base.AbstractSimpleAsn1Item.tagSet.clone(tagId=0x01)
    allowedTypes = ( IntType, LongType )
    subtypeConstraints = ( subtypes.SingleValueConstraint(0, 1), )
    initialValue = 0

    # Basic logical ops
    
    def __and__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        return self.__class__(self.get() & value.get())

    __rand__ = __and__

    def __or__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        return self.__class__(self.get() | value.get())

    __ror__ = __or__

    def __xor__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        return self.__class__(self.get() ^ value.get())

    __rxor__ = __xor__

    def __iand__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        self.set(self.get() & value.get())
        return self

    def __ior__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        self.set(self.get() | value.get())
        return self

    def __ixor__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        self.set(self.get() ^ value.get())
        return self

class Integer(base.AbstractSimpleAsn1Item):
    tagSet = base.AbstractSimpleAsn1Item.tagSet.clone(tagId=0x02)
    allowedTypes = ( IntType, LongType, StringType )
    namedValues = namedval.NamedValues()
    initialValue = 0

    def __str__(self):
        r = self.namedValues.getName(self.rawAsn1Value)
        if r is not None:
            return '%s(%s)' % (r, self.rawAsn1Value)
        else:
            return str(self.rawAsn1Value)
        
    # Basic arithmetic ops
    
    def __add__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        return self.__class__(self.get() + value.get())

    __radd__ = __add__
    
    def __sub__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        return self.__class__(self.get() - value.get())

    def __rsub__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        return self.__class__(value.get() - self.get())
    
    def __mul__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        return self.__class__(self.get() * value.get())

    __rmul__ = __mul__
    
    def __div__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        return self.__class__(self.get() / value.get())

    def __rdiv__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        return self.__class__(value.get() / self.get())

    def __mod__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        return self.__class__(self.get() % value.get())

    __rmod__ = __mod__

    def __pow__(self, value, modulo):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        return self.__class__(pow(self.get(), value.get(), modulo))

    def __rpow__(self, value, modulo):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        return self.__class__(pow(value.get(), self.get(), modulo))

    def __lshift__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        return self.__class__(self.get() << value.get())

    def __rshift__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        return self.__class__(self.get() >> value.get())

    def __and__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        return self.__class__(self.get() & value.get())

    __rand__ = __and__

    def __or__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        return self.__class__(self.get() | value.get())

    __ror__ = __or__

    def __xor__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        return self.__class__(self.get() ^ value.get())

    __rxor__ = __xor__

    def __iadd__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        self.set(self.get() + value.get())
        return self

    # For Python 1.5 which does not yet support +=
    inc = __iadd__
    
    def __isub__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        self.set(self.get() - value.get())
        return self

    # For Python 1.5 which does not yet support -=
    dec = __isub__
    
    def __imul__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        self.set(self.get() * value.get())
        return self

    # For Python 1.5 which does not yet support *=
    mul = __imul__
    
    def __idiv__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        self.set(self.get() / value.get())
        return self

    # For Python 1.5 which does not yet support /=
    div = __idiv__
    
    def __imod__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        self.set(self.get() % value.get())
        return self

    def __ipow__(self, value, modulo):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        self.set(pow(self.get(), value.get(), modulo))
        return self

    def __ilshift__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        self.set(self.get() << value.get())
        return self
    
    def __irshift__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        self.set(self.get() >> value.get())
        return self

    def __iand__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        self.set(self.get() & value.get())
        return self

    def __ior__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        self.set(self.get() | value.get())
        return self

    def __ixor__(self, value):
        if not isinstance(value, self.__class__):
            value = self.componentFactoryBorrow(value)
        self.set(self.get() ^ value.get())
        return self

    def __int__(self): return int(self.get())

    def __long__(self): return long(self.get())

    def __float__(self): return float(self.get())    

    def _iconv(self, value):
        if type(value) != StringType:
            return value
        r = self.namedValues.getValue(value)
        if r is not None:
            return r
        try:
            return atoi(value)
        except:
            try:
                return atol(value)
            except:
                raise error.BadArgumentError(
                    'Cant coerce %s into integer' % value
                    )

    def addNamedValues(self, *namedValues):
        self.namedValues = apply(self.namedValues.clone, namedValues)
        return self

class BitString(base.AbstractSimpleAsn1Item):
    tagSet = base.AbstractSimpleAsn1Item.tagSet.clone(tagId=0x03)
    allowedTypes = ( StringType, )
    initialValue = ''

class OctetString(base.AbstractSimpleAsn1Item):
    tagSet = base.AbstractSimpleAsn1Item.tagSet.clone(tagId=0x04)
    allowedTypes = ( StringType, )
    initialValue = ''
    
    # Immutable sequence object protocol
    
    def __len__(self): return len(self.get())
    def __getitem__(self, i):
        if type(i) == SliceType:
            return self.__class__(getslice(self.get(), i.start, i.stop))
        else:
            return self.get()[i]

    def __add__(self, other):
        val = self.get() + self.componentFactoryBorrow(other).get()
        return self.__class__(val)

    def __radd__(self, other):
        val = self.componentFactoryBorrow(other) + self.rawAsn1Value
        return self.__class__(val) 

    def __mul__(self, value): return self.__class__(self.get() * value)

    __rmul__ = __mul__

    # They won't be defined if version is at least 2.0 final
    if base.version_info < (2, 0):
        def __getslice__(self, i, j):
            return self[max(0, i):max(0, j):]

class Null(base.AbstractSimpleAsn1Item):
    tagSet = base.AbstractSimpleAsn1Item.tagSet.clone(tagId=0x05)
    allowedTypes = ( IntType, LongType, StringType, NoneType )
    subtypeConstraints = ( subtypes.SingleValueConstraint(0, 0L, '', None), )
    initialValue = 0
    
    def _iconv(self, value):
        if value: return 1
        else: return 0

class ObjectIdentifier(base.AbstractSimpleAsn1Item):
    tagSet = base.AbstractSimpleAsn1Item.tagSet.clone(tagId=0x06)
    allowedTypes = ( StringType, TupleType, ListType )
    initialValue = ()
    
    # Sequence object protocol
    
    def __len__(self): return len(self.rawAsn1Value)
    def __getitem__(self, i):
        if type(i) == SliceType:
            vals = filter(None, split(self.get(), '.'))
            return self.__class__(join(getslice(vals, i.start,
                                                       i.stop), '.'))
        else:
            return self.rawAsn1Value[i]

    def __add__(self, other):
        return self.__class__(self.get() + \
                              self.componentFactoryBorrow(other).get())

    def __radd__(self, other):
        return self.__class__(self.componentFactoryBorrow(other).get() + \
                              self.get())

    # They won't be defined if version is at least 2.0 final
    if base.version_info < (2, 0):
        def __getslice__(self, i, j):
            return self[max(0, i):max(0, j):]

    def index(self, suboid): return val.index(self.rawAsn1Value)

    def isaprefix(self, other):
        """
           isaprefix(other) -> boolean
           
           Compare our own OID with the other one (given as a string),
           return non-None if ours is a prefix of the other OID.

           This is intended to be used for MIB tables retrieval.
        """
        # Normalize foreign value type to ours
        if not isinstance(other, self.__class__):
            other = self.componentFactoryBorrow(other)

        # Pick the shortest oid
        if len(self) <= len(other):
            # Get the length
            length = len(self)

            # Compare oid'es
            if self.rawAsn1Value[:length] == other.rawAsn1Value[:length]:
                return not None

    def match(self, subOids, offset=None):
        """Compare OIDs by numeric values"""
        # The following is a bit kludgy as we have to support a part of
        # OID syntax here (which is also being done by ASN.1 object input
        # filter) but so far I do not see any better solution XXX (cmp?)
        if type(subOids) == StringType:
            try:
                subOids = filter(lambda x: len(x), split(subOids, '.'))
            except:
                raise error.BadArgumentError(
                    'Malformed Object ID %s at %s' %
                    (str(subOids), self.__class__.__name__)
                )
            for idx in range(len(subOids)):
                try:
                    subOids[idx] = ObjectIdentifier(subOids[idx])[0]
                except error.BadArgumentError:
                    pass
        else:
            subOids = tuple(ObjectIdentifier(subOids))            

        if offset is None:
            offset = max(len(self), len(subOids))
        if len(self) < offset or len(subOids) < offset:
            return -1

        for idx in range(offset):
            if self[idx] == subOids[idx]:
                continue
            return -1
        else:
            return 0
        
    def str2num(self, symbolicOid):
        """
            str2num(symbolicOid) -> numericOid
            
            Convert symbolic Object ID presented in a dotted form into a
            numeric Object ID  represented as a list of numeric sub-ID's.
        """
        numericOid = ()
        
        if not symbolicOid:
            return numericOid

        for element in filter(None, split(symbolicOid, '.')):
            try:
                numericOid = numericOid + (atoi(element, 0), )
            except string.atoi_error:
                try:
                    numericOid = numericOid + (atol(element, 0), )
                except string.atol_error, why:                        
                    raise error.BadArgumentError(
                        'Malformed Object ID %s at %s: %s' %
                        (str(symbolicOid), self.__class__.__name__, why)
                        )
        return numericOid

    def num2str(self, numericOid):
        """
            num2str(numericOid) -> symbolicOid
            
            Convert numeric Object ID presented as a list of numeric
            sub-ID's into symbolic Object ID in dotted notation.
        """
        symbolicOid = ''
        if not numericOid: return symbolicOid

        # Convert a list of number into a list of symbols and merge all
        # list members into a string
        try:
            idx = 0
            while idx < len(numericOid):
                oid = str(numericOid[idx])
                if numericOid[idx] <= 0x7fffffff:
                    if oid[-1] == 'L': oid = oid[:-1]
                symbolicOid = symbolicOid + '.' + oid
                idx = idx + 1
                    
        except StandardError, why:
            raise error.BadArgumentError(
                'Malformed OID %s at %s: %s' % 
                (numericOid, self.__class__.__name__, why)
            )
        if not symbolicOid:
            raise error.BadArgumentError(
                'Empty numeric Object ID %s at %s' %
                (str(numericOid), self.__class__.__name__)
            )
        return symbolicOid

    def _iconv(self, value):
        if type(value) == StringType:
            return self.str2num(value)
        if type(value) == ListType:
            value = tuple(value)
        if type(value) == TupleType:
            return self.str2num(self.num2str(value))
        return value
    
    def _oconv(self, value):
        return self.num2str(value)

class Real(base.AbstractSimpleAsn1Item):
    tagSet = base.AbstractSimpleAsn1Item.tagSet.clone(tagId=0x09)
    allowedTypes = ( IntType, LongType, FloatType )
    initialValue = 0.0

class Enumerated(base.AbstractSimpleAsn1Item):
    tagSet = base.AbstractSimpleAsn1Item.tagSet.clone(tagId=0x10)
    allowedTypes = ( IntType, LongType )
    initialValue = 0

# "Structured" ASN.1 types implementation

class Set(base.AbstractMappingAsn1Item):
    tagSet = base.AbstractMappingAsn1Item.tagSet.clone(tagId=0x11)
    protoComponents = {}

    def __init__(self, **kwargs):
        base.AbstractMappingAsn1Item.__init__(self)
        # Initialize fixed structure
        if self.protoComponents:
            for k, v in self.protoComponents.items():
                self._components[k] = v.clone()
        if kwargs: self.update(kwargs)

    def __setitem__(self, key, value):
        protoValue = self.protoComponents.get(key, None)
        if protoValue is None:
            raise error.BadArgumentError(
                'No such key %s at %s' %
                (key, self.__class__.__name__)
            )
        if protoValue.isSubtype(value):
            self.verifyConstraints(value)
            self._components[key] = value
        else:
            raise error.BadArgumentError(
                'Unexpected component type %s at %s' %
                (value.__class__.__name__, self.__class__.__name__)
            )

class Sequence(Set):
    tagSet = Set.tagSet.clone(tagId=0x10)
    protoSequence = ()

    # Provisions for ordered dictionary
    def keys(self): return list(self.protoSequence)
    def values(self):
        return map(lambda k, v=self._components: v[k], self.protoSequence)
    def items(self):
        return map(lambda k, v=self._components: (k, v[k]), self.protoSequence)

class Choice(base.AbstractMappingAsn1Item):
    tagSet = base.AbstractMappingAsn1Item.tagSet.clone(
        tagCategory=tags.tagCategoryUntagged
        )
    protoComponents = {}
    initialComponentKey = None
    
    def __init__(self, **kwargs):
        base.AbstractMappingAsn1Item.__init__(self)
        if kwargs:
            if len(kwargs) == 1:
                self.update(kwargs)
            else:
                raise error.BadArgumentError(
                    'Too many components given at %s' % self
                )
        else:
            key = self.initialComponentKey
            if key:
                self._components[key] = self.protoComponents[key].clone()

    def componentFactoryBorrow(self, key):
        if not hasattr(self, '_componentCache'):
            self._componentCache = {}
        if not self._componentCache.has_key(key):
            val = self.protoComponents.get(key, None)
            if val is None:
                raise error.BadArgumentError('Non-existing key %s' % key)
            self._componentCache[key] = self.protoComponents[key].clone()
        return self._componentCache[key]

    # Dictionary interface emulation (for strict ordering)

    def __setitem__(self, key, value):
        protoValue = self.protoComponents.get(key, None)
        if protoValue is None:
            raise error.BadArgumentError(
                'No such key %s at %s' %
                (key, self.__class__.__name__)
            )
        if protoValue.isSubtype(value):
            self._components.clear()
            self.verifyConstraints(value)
            self._components[key] = value
        else:
            raise error.BadArgumentError(
                'Unregistered component %s at %s' %
                (value.__class__.__name__, self.__class__.__name__)
            )

    def __delitem__(self, key):
        if self._components.has_key(key):
            del self._components[key]

class SequenceOf(base.AbstractSequenceAsn1Item):
    tagSet = base.AbstractSequenceAsn1Item.tagSet.clone(tagId=0x10)
    protoComponent = None
    initialValue = []

class SetOf(SequenceOf):
    tagSet = SequenceOf.tagSet.clone(tagId=0x11)

if __name__ == '__main__':
    i = Integer()
    i.namedValues = i.namedValues.clone('up', ('down', 2))
    i.set('up')
    print str(i)
