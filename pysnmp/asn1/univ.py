"""
   ASN.1 "universal" data types.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'Boolean', 'Integer', 'BitString', 'OctetString', 'Null', \
            'ObjectIdentifier', 'Real', 'Enumerated', 'Sequence', \
            'SequenceOf', 'Set', 'SetOf', 'Choice' ]

import string
from operator import getslice, setslice, delslice
from types import IntType, LongType, StringType, NoneType, FloatType,  \
     ListType, SliceType
from exceptions import StandardError, TypeError
from pysnmp.asn1 import base, error

#
# ASN.1 "simple" types implementation
#

class Boolean(base.SimpleAsn1Object):
    """An ASN.1 boolean object
    """
    tagId = 0x01
    allowedTypes = [ IntType, LongType ]
    singleValueConstraint = [ 0, 1 ]
    initialValue = 0L

    # Disable not applicible constraints
    _subtype_value_range_constraint = None
    _subtype_size_constraint = None
    _subtype_permitted_alphabet_constraint = None

    # Basic logical ops
    
    def __and__(self, value):
        """Perform binary AND operation
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        return self.__class__(self.get() & value.get())

    __rand__ = __and__

    def __or__(self, value):
        """Perform binary OR operation
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        return self.__class__(self.get() | value.get())

    __ror__ = __or__

    def __xor__(self, value):
        """Perform binary XOR operation
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        return self.__class__(self.get() ^ value.get())

    __rxor__ = __xor__

    def __iand__(self, value):
        """Perform binary AND operation against ourselves
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        self.set(self.get() & value.get())
        return self

    def __ior__(self, value):
        """Perform binary OR operation against ourselves
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        self.set(self.get() | value.get())
        return self

    def __ixor__(self, value):
        """Perform binary XOR operation against ourselves
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        self.set(self.get() ^ value.get())
        return self

class Integer(base.SimpleAsn1Object):
    """An ASN.1, indefinite length integer object
    """
    tagId = 0x02
    allowedTypes = [ IntType, LongType ]
    initialValue = 0L

    # Disable not applicible constraints
    _subtype_size_constraint = None
    _subtype_permitted_alphabet_constraint = None

    # Basic arithmetic ops
    
    def __add__(self, value):
        """Add a value
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        return self.__class__(self.get() + value.get())

    __radd__ = __add__
    
    def __sub__(self, value):
        """Subscract a value
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        return self.__class__(self.get() - value.get())

    def __rsub__(self, value):
        """Subscract our value from given one
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        return self.__class__(value.get() - self.get())
    
    def __mul__(self, value):
        """Multiply a value
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        return self.__class__(self.get() * value.get())

    __rmul__ = __mul__
    
    def __div__(self, value):
        """Divide a value by ourselves
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        return self.__class__(self.get() / value.get())

    def __rdiv__(self, value):
        """Divide ourselves by value
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        return self.__class__(value.get() / self.get())

    def __mod__(self, value):
        """Take a modulo of ourselves
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        return self.__class__(self.get() % value.get())

    __rmod__ = __mod__

    def __pow__(self, value, modulo):
        """Provision for pow()
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        return self.__class__(pow(self.get(), value.get(), modulo))

    def __rpow__(self, value, modulo):
        """Provision for rpow()
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        return self.__class__(pow(value.get(), self.get(), modulo))

    def __lshift__(self, value):
        """Perform left shift operation
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        return self.__class__(self.get() << value.get())

    def __rshift__(self, value):
        """Perform right shift operation
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        return self.__class__(self.get() >> value.get())

    def __and__(self, value):
        """Perform binary AND operation
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        return self.__class__(self.get() & value.get())

    __rand__ = __and__

    def __or__(self, value):
        """Perform binary OR operation
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        return self.__class__(self.get() | value.get())

    __ror__ = __or__

    def __xor__(self, value):
        """Perform binary XOR operation
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        return self.__class__(self.get() ^ value.get())

    __rxor__ = __xor__

    def __iadd__(self, value):
        """Add value to ourselves
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        self.set(self.get() + value.get())
        return self

    # For Python 1.5 which does not yet support +=
    inc = __iadd__
    
    def __isub__(self, value):
        """Subscract value from ourselves
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        self.set(self.get() - value.get())
        return self

    # For Python 1.5 which does not yet support -=
    dec = __isub__
    
    def __imul__(self, value):
        """Multiply a value to ourselves
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        self.set(self.get() * value.get())
        return self

    # For Python 1.5 which does not yet support *=
    mul = __imul__
    
    def __idiv__(self, value):
        """Divide a value by ourselves
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        self.set(self.get() / value.get())
        return self

    # For Python 1.5 which does not yet support /=
    div = __idiv__
    
    def __imod__(self, value):
        """Take a modulo of ourselves
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        self.set(self.get() % value.get())
        return self

    def __ipow__(self, value, modulo):
        """Provision for x**=y
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        self.set(pow(self.get(), value.get(), modulo))
        return self

    def __ilshift__(self, value):
        """Perform left shift operation
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        self.set(self.get() << value.get())
        return self
    
    def __irshift__(self, value):
        """Perform right shift operation
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        self.set(self.get() >> value.get())
        return self

    def __iand__(self, value):
        """Perform binary AND operation against ourselves
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        self.set(self.get() & value.get())
        return self

    def __ior__(self, value):
        """Perform binary OR operation against ourselves
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        self.set(self.get() | value.get())
        return self

    def __ixor__(self, value):
        """Perform binary XOR operation against ourselves
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        self.set(self.get() ^ value.get())
        return self

    def __int__(self):
        """Return an integer value of ourselves
        """
        return int(self.get())

    def __long__(self):
        """Return a long integer value of ourselves
        """
        return long(self.get())

    def __float__(self):
        """Return a floating point value of ourselves
        """
        return float(self.get())    

class BitString(base.SimpleAsn1Object):
    """An ASN.1 BITSTRING object XXX
    """
    tagId = 0x03
    allowedTypes = [ StringType ]

    # Disable not applicible constraints
    _subtype_value_range_constraint = None
    _subtype_permitted_alphabet_constraint = None

class OctetString(base.SimpleAsn1Object):
    """ASN.1 octet string object
    """
    tagId = 0x04
    allowedTypes = [ StringType ]
    initialValue = ''
    
    # Disable not applicible constraints
    _subtype_value_range_constraint = None
    _subtype_permitted_alphabet_constraint = None

    # Immutable sequence object protocol
    
    def __len__(self): return len(self.get())
    def __getitem__(self, i):
        """Get string component by index or slice
        """
        if type(i) == SliceType:
            return self.__class__(getslice(self.get(), i.start, i.stop))
        else:
            return self.get()[i]

    def __add__(self, other):
        """Add sub-id  with input verification
        """
        val = self.get() + self.__class__(other).get()
        return self.__class__(val)

    def __radd__(self, other):
        """Add sub-id  with input verification
        """
        val = list(self.__class__(other)) + self.rawAsn1Value
        return self.__class__(val) 

    def __mul__(self, value):
        """Multiply a value
        """
        return self.__class__(self.get() * value)

    __rmul__ = __mul__

    # They won't be defined if version is at least 2.0 final
    def __getslice__(self, i, j):
        return self[max(0, i):max(0, j):]

class Null(base.SimpleAsn1Object):
    """ASN.1 NULL object
    """
    tagId = 0x05
    allowedTypes = [ IntType, LongType, StringType, NoneType ]
    singleValueConstraint = [ 0, 0L, '', None ]

    # Disable not applicible constraints
    _subtype_contained_subtype_constraint = None
    _subtype_value_range_constraint = None
    _subtype_size_constraint = None
    _subtype_permitted_alphabet_constraint = None

class ObjectIdentifier(base.SimpleAsn1Object):
    """ASN.1 Object ID object (taken and returned as string in conventional
       "dotted" representation)
    """
    tagId = 0x06
    allowedTypes = [ StringType, ListType ]
    initialValue = []
    initialChildren = []
    
    # Disable not applicible constraints
    _subtype_value_range_constraint = None
    _subtype_size_constraint = None
    _subtype_permitted_alphabet_constraint = None

    def __init__(self, value=None):
        """
        """
        base.SimpleAsn1Object.__init__(self, value)
        self.childNodes = None

    # Sequence object protocol
    
    def __len__(self): return len(self.rawAsn1Value)
    def __getitem__(self, i):
        """Get sequence component by index or slice
        """
        if type(i) == SliceType:
            vals = filter(None, string.split(self.get(), '.'))
            return self.__class__(string.join(getslice(vals, i.start,
                                                       i.stop), '.'))
        else:
            return self.rawAsn1Value[i]

    def __delitem__(self, i):
        """Delete sequence component by index or slice
        """
        vals = filter(None, string.split(self.get(), '.'))
        if type(i) == SliceType:
            delslice(vals, i.start, i.stop)
        else:
            del vals[i]
        self.set(string.join(vals, '.'))
        
    def __setitem__(self, i, item):
        """Set sub-id by index or slice with input verification
        """
        vals = filter(None, string.split(self.get(), '.'))
        if type(i) == SliceType:
            setslice(vals, i.start, i.stop,
                     filter(None,string.split(self.__class__([item]).get())))
        else:
            vals[i] = self.__class__([item]).get()
        self.set(string.join(vals, '.'))

    def __add__(self, other):
        """Add sub-id  with input verification
        """
        return self.__class__(self.get() + self.__class__(other).get())

    def __radd__(self, other):
        """Add sub-id  with input verification
        """
        return self.__class__(self.__class__(other).get() + self.get())

    # They won't be defined if version is at least 2.0 final
    def __getslice__(self, i, j):
        return self[max(0, i):max(0, j):]
    def __setslice__(self, i, j, seq):
        self[max(0, i):max(0, j):] = seq
    def __delslice__(self, i, j):
        del self[max(0, i):max(0, j):]

    def append(self, item):
        """Append sub-id with input verification
        """
        self.set(self.get() + '.' + str(item))

    def extend(self, item):
        """Append an oid with input verification
        """
        self.set(self.get() + self.__class__(item).get())        

    def index(self, suboid):
        """Returns index of first occurrence of given sub-identifier
        """
        val = list(self)
        return val.index(suboid)

    def isaprefix(self, other):
        """
           isaprefix(other) -> boolean
           
           Compare our own OID with the other one (given as a string),
           return non-None if ours is a prefix of the other OID.

           This is intended to be used for MIB tables retrieval.
        """
        # Normalize foreign value type to ours
        if not isinstance(other, self.__class__):
            other = self.__class__(other)

        # Pick the shortest oid
        if len(self) <= len(other):
            # Get the length
            length = len(self)

            # Compare oid'es
            if self.rawAsn1Value[:length] == other.rawAsn1Value[:length]:
                return not None

    def match(self, subOids, offset=None):
        """Compare OIDs by numeric or alias values
        """
        # The following is a bit kludgy as we have to support a part of
        # OID syntax here (which is also being done by ASN.1 object input
        # filter) but so far I do not see any better solution XXX (cmp?)
        if type(subOids) == StringType:
            try:
                subOids = filter(lambda x: len(x), string.split(subOids, '.'))
            except:
                raise error.BadArgumentError('Malformed Object ID %s at %s' % (str(subOids), self.__class__.__name__))
            for idx in range(len(subOids)):
                try:
                    subOids[idx] = ObjectIdentifier(subOids[idx])[0]
                except error.BadArgumentError:
                    pass
        else:
            subOids = list(ObjectIdentifier(subOids))            

        if offset is None:
            offset = max(len(self), len(subOids))
        if len(self) < offset or len(subOids) < offset:
            return -1

        for idx in range(offset):
            if self[idx] == subOids[idx] or self.aliases[idx] == subOids[idx]:
                continue
            return -1
        else:
            return 0
        
    def str2num(self, symbolicOid, aliases=None):
        """
            str2num(symbolicOid) -> numericOid
            
            Convert symbolic Object ID presented in a dotted form into a
            numeric Object ID  represented as a list of numeric sub-ID's.
        """
        numericOid = []
        
        if len(symbolicOid) == 0:
            return numericOid

        try:
            # Fast lane for all-numeric OIDs
            if string.find(symbolicOid, '(') < 0:
                for element in filter(None, string.split(symbolicOid, '.')):
                    numericOid.append(string.atol(element, 0))
                if aliases is not None:
                    aliases.extend([None] * len(numericOid))
            else:
                for element in filter(None, string.split(symbolicOid, '.')):
                    if string.find(element, '(') < 0:
                        numericOid.append(string.atol(element, 0))
                        if aliases is not None: aliases.append(None)
                    else:
                        idx = string.index(element, '(')
                        if aliases is not None:
                            aliases.append(string.strip(element[:idx]))
                        element = string.strip(element[idx+1:string.rindex(element, ')')])
                        numericOid.append(string.atol(element, 0))

        except string.atol_error, why:
            raise error.BadArgumentError('Malformed Object ID %s at %s: %s' %\
                                         (str(symbolicOid),
                                          self.__class__.__name__, why))
        return numericOid

    def num2str(self, numericOid, aliases=None):
        """
            num2str(numericOid) -> symbolicOid
            
            Convert numeric Object ID presented as a list of numeric
            sub-ID's into symbolic Object ID in dotted notation.
        """
        symbolicOid = ''
        if len(numericOid) == 0:
            return symbolicOid

        # Convert a list of number into a list of symbols and merge all
        # list members into a string
        try:
            for idx in range(len(numericOid)):
                oid = str(numericOid[idx])
                if numericOid[idx] <= 0x7fffffff:
                    if oid[-1] == 'L': oid = oid[:-1]
                if aliases is None or len(aliases)-1 < idx or aliases[idx] is None:
                    symbolicOid = symbolicOid + '.' + oid
                else:
                    symbolicOid = '%s.%s(%s)' % (symbolicOid, aliases[idx], oid)
                    
        except StandardError, why:
            raise error.BadArgumentError('Malformed OID %s at %s: %s'
                                         % (numericOid,
                                            self.__class__.__name__,
                                            why))
        if not symbolicOid:
            raise error.BadArgumentError('Empty numeric Object ID %s at %s' %\
                                         (str(numericOid),
                                          self.__class__.__name__))
        return symbolicOid

    def _iconv(self, value):
        """Input filter: accept both string & list type OIDs
        """
        if type(value) == StringType:
            self.aliases = []
            return self.str2num(value, self.aliases)
        if type(value) == ListType:
            self.aliases = None
            return self.str2num(self.num2str(value, self.aliases),
                                self.aliases)

    def _oconv(self, value): return self.num2str(value, self.aliases)

    # Provision for hierarchical organisation

    def initChildNodes(self):
        """Initialize possible children
        """
        self.childNodes = {}        
        for newNode in self.initialChildren:
            self.attachNode(newNode())
        
    def resolveKeyOid(self, arg):
        if hasattr(arg, 'getKeyOid'):
            getKeyOid = getattr(arg, 'getKeyOid')
            if not callable(getKeyOid):
                raise error.BadArgumentError('Non-callable %s.getKeyOid() at %s' % (arg, self))
            return getKeyOid()
        else:
            return arg

    def searchNode(self, oid, idx=None):
        """Search the tree of OIDs by name
        """
        if self.childNodes is None: self.initChildNodes()
        if not isinstance(oid, ObjectIdentifier):
            oid = ObjectIdentifier(oid)
        if idx is None:
            idx = len(self)
        childNode = self.childNodes.get(oid[idx], None)
        if childNode is None:
            raise error.BadArgumentError('No such sub-OID %s under %s at %s' %\
                                         (str(oid), self,
                                          self.__class__.__name__))
        childOid = self.resolveKeyOid(childNode)
        if oid.rawAsn1Value == childOid.rawAsn1Value:
            return childNode
        else:
            return childOid.searchNode(oid, idx+1)

    def attachNode(self, newNode, newOid=None, idx=None):
        """Attach a new OID node to OIDs tree
        """
        if self.childNodes is None: self.initChildNodes()
        if newOid is None:
            newOid = self.resolveKeyOid(newNode)
            if not isinstance(newOid, ObjectIdentifier):
                raise error.BadArgumentError('Child node %s is not an ObjectIdentifier type at %s' % (newOid, self))
        if idx is None:
            if len(newOid) <= len(self):
                raise error.BadArgumentError('Cannot attach %s to parent OID at %s' % (newOid, self))
            idx = len(self)
        if len(newOid) - 1 == idx:
            self.childNodes[newOid[idx]] = newNode
            return
        if not self.childNodes.has_key(newOid[idx]):
            self.childNodes[newOid[idx]] = ObjectIdentifier(self.get() + newOid[idx:idx+1].get())
        childNode = self.childNodes[newOid[idx]]
        self.resolveKeyOid(childNode).attachNode(newNode, newOid, idx + 1)

    def strNode(self, level=0):
        """Pretty print OID tree
        """
        if self.childNodes is None: self.initChildNodes()
        out = ''
        for childNode in self.childNodes.values():
            out = out + '> ' + repr(childNode) + '\n' + \
                  self.resolveKeyOid(childNode).strNode()
        return out
        
class Real(base.SimpleAsn1Object):
    """An ASN.1 REAL object XXX
    """
    tagId = 0x09
    allowedTypes = [ IntType, LongType, FloatType ]
    initialValue = 0.0

    # Disable not applicible constraints
    _subtype_size_constraint = None
    _subtype_permitted_alphabet_constraint = None

class Enumerated(base.SimpleAsn1Object):
    """An ASN.1 ENUMERATED object XXX
    """
    tagId = 0x10
    allowedTypes = [ IntType, LongType ]
    initialValue = 0

    # Disable not applicible constraints
    _subtype_value_range_constraint = None
    _subtype_size_constraint = None
    _subtype_permitted_alphabet_constraint = None

#
# ASN.1 "structured" types implementation
#

class Sequence(base.RecordTypeAsn1Object):
    """ASN.1 SEQUENCE object
    """
    tagId = 0x10

class SequenceOf(base.VariableTypeAsn1Object):
    """ASN.1 SEQUENCE OF object
    """
    tagId = 0x10

    # Disable not applicible constraints
    _subtype_permitted_alphabet_constraint =None

class Set(base.RecordTypeAsn1Object):
    """ASN.1 SET object
    """
    tagId = 0x11

class SetOf(base.VariableTypeAsn1Object):
    """ASN.1 SET OF object
    """
    tagId = 0x11

    # Disable not applicible constraints
    _subtype_permitted_alphabet_constraint = None

class Choice(base.ChoiceTypeAsn1Object):
    """ASN.1 CHOICE clause
    """
    # Untagged type
    tagCategory = base.tagCategories['UNTAGGED']
    
    # Disable not applicible constraints XXX
    _subtype_permitted_alphabet_constraint = None

class Any(base.AnyTypeAsn1Object):
    """ASN.1 ANY clause
    """
    # Untagged type
    tagCategory = base.tagCategories['UNTAGGED']
    
    # Disable not applicible constraints XXX
    _subtype_permitted_alphabet_constraint = None
    _subtype_inner_subtype_constraint = None
