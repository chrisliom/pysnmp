"""A framework for implementing ASN.1 data types"""
try:
    from sys import version_info
except ImportError:
    version_info = ( 0, 0 )   # a really early version
version_info_major, version_info_minor = version_info[:2]
from operator import getslice, setslice, delslice
from string import join
from types import *
from pysnmp.asn1 import tags, subtypes, error
from pysnmp.error import PySnmpError

class Asn1Item: pass

class Asn1ItemBase(Asn1Item):
    # Set of tags for this ASN.1 type
    tagSet = tags.TagSet(
        tags.tagClassUniversal, tags.tagFormatSimple, 0,
        tags.tagCategoryImplicit
        )
    
    # Initializer type constraint
    allowedTypes = ()

    # A list of subtypes.Constraint instances for checking values
    # initial XXX
    subtypeConstraints = ()

    # Allowed types verification
    if version_info_major < 2 or version_info_major == 2 \
       and version_info_minor < 2:
        def verifyConstraints(self, value):
            if self.allowedTypes:
                for allowedType in self.allowedTypes:
                    if isinstance(value, allowedType):
                        break
                else:
                    raise error.ValueConstraintError(
                        'Value type constraint for %s: %s not in %s' %
                        (self.__class__.__name__, type(value),
                         self.allowedTypes)
                    )
            # Contraints verification
            for c in self.subtypeConstraints: c(self, value)
    else:
        def verifyConstraints(self, value):
            if self.allowedTypes:
                if not isinstance(value, self.allowedTypes):
                    raise error.ValueConstraintError(
                        'Value type constraint for %s: %s not in %s' %
                        (self.__class__.__name__, type(value),
                         self.allowedTypes)
                    )

            # Contraints verification
            for c in self.subtypeConstraints: c(self, value)

    def isSubtype(self, other):
        """Returns true if the given instance is a ASN1 subtype of ourselves"""
        if isinstance(other, Asn1Item):
            # XXX is it always correct?
            for t in self.tagSet:
                if t not in other.tagSet:
                    return
            for c in self.subtypeConstraints:
                if c not in other.subtypeConstraints:
                    return
            return 1

    def addConstraints(self, *constraints):
        """Add more ASN1 subtype constraints to this object"""
        self.subtypeConstraints = self.subtypeConstraints + constraints
        return self
        
    def clone(self):
        """Returns a new instance of this class with ASN1 subtype-sensitive
           attributes inherited from this class instance
        """   
        c = self.__class__()

        # Inherit tags
        c.tagSet = self.tagSet.clone()

        # Inherit types
        c.allowedTypes = self.allowedTypes

        # Inherit subtypes
        c.subtypeConstraints = self.subtypeConstraints

        return c

# Base class for a simple ASN.1 object. Defines behaviour and
# properties of various non-structured ASN.1 objects.        
class AbstractSimpleAsn1Item(Asn1ItemBase):
    tagSet = Asn1ItemBase.tagSet.clone(
        tagFormat=tags.tagFormatSimple, tagId=0x00
        )
    initialValue = None # no constraints checks
    
    def __init__(self, value=None):
        if value is None:
            initialValue = self.initialValue            
            if callable(initialValue):
                initialValue()
            else:
                self.rawAsn1Value = initialValue
            return
        else:
            self.set(value)

    def __repr__(self):
        return self.__class__.__name__ + '(' + repr(self.get()) + ')'

    def __str__(self): return str(self.get())
    def __cmp__(self, other):
        if isinstance(other, AbstractSimpleAsn1Item):
            if not isinstance(other, self.__class__):
                try:
                    other = self.componentFactoryBorrow(other.get())
                except PySnmpError:
                    # Hide coercion errors
                    return -1
        else:
            try:
                other = self.componentFactoryBorrow(other)
            except PySnmpError:
                # Hide coercion errors
                return -1
        return cmp(self.rawAsn1Value, other.rawAsn1Value)

    # XXX invalid?
#    def __hash__(self):
#        return hash((self.rawAsn1Value, self.tagClass, self.tagFormat,
#                     self.tagId, self.tagCategory))

    def __nonzero__(self):
        if self.rawAsn1Value:
            return 1
        else:
            return 0
    
    def componentFactoryBorrow(self, value=None):
        if not hasattr(self, '_componentCache'):
            self._componentCache = self.clone()
        if value is not None:
            self._componentCache.set(value)
        return self._componentCache
        
    #
    # Simple ASN.1 object protocol definition
    #

    def set(self, value):
        """Set a value to object"""
        # Allow initalization from instances
        if isinstance(value, AbstractSimpleAsn1Item):
            # Save on same-type instances
            if isinstance(value, self.__class__):
                value = value.rawAsn1Value
            else:
                value = value.get()
                f = getattr(self, '_iconv', None)
                if f is not None:
                    value = f(value)
        else:
            f = getattr(self, '_iconv', None)
            if f is not None:
                value = f(value)

        self.verifyConstraints(value)

        if isinstance(value, ListType):
            # Copy [mutable] list
            self.rawAsn1Value = value[:]
        else:
            self.rawAsn1Value = value

        # Handy for comparation and thelikes
        return self
            
    def get(self):
        """Get a value from object"""
        f = getattr(self, '_oconv', None)
        if f is not None:
            return f(self.rawAsn1Value)
        return self.rawAsn1Value

    # XXX left for compatibility
    def getTerminal(self): return self

class StructuredAsn1ItemBase(Asn1ItemBase):
    tagSet = Asn1ItemBase.tagSet.clone(
        tagFormat=tags.tagFormatConstructed
        )

class AbstractMappingAsn1Item(StructuredAsn1ItemBase):
    allowedTypes = ( Asn1Item, )

    def __init__(self):
        self._components = {}
        
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,
                           join(map(lambda (k, v): '%s=%s' % (k, repr(v)),
                                    self.items()), ',')
                 )

    def __nonzero__(self):
        if self._components: return 1
        else: return 0

    def __cmp__(self, other):
        if type(other) == InstanceType and isinstance(
            other, AbstractMappingAsn1Item
            ):
            return cmp(self.items(), other.items())
        else:
            # Hide coercion errors
            return -1

    # Mapping object protocol
    def __getitem__(self, key): return self._components[key]
    def keys(self): return self._components.keys()
    def has_key(self, key): return self._components.has_key(key)
    def values(self): return self._components.values()
    def items(self): return self._components.items()
    def update(self, dict): self._components.update(dict)
    def get(self, key, default=None): return self._components.get(key, default)
    def __len__(self): return len(self._components)

class AbstractSequenceAsn1Item(StructuredAsn1ItemBase):
    def __init__(self, *args):
        self._components = []
        if args:
            self.extend(args)
        else:
            for val in self.initialValue:
                self._components.append(val.clone())

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,
                           join(map(repr, self._components), ',')
                 )

    def __cmp__(self, other):
        if type(other) == InstanceType and isinstance(
            other, AbstractSequenceAsn1Item
            ):
            return cmp(self._components, other._components)
        else:
            # Hide coercion errors
            return -1

    def componentFactoryBorrow(self):
        if self.protoComponent is None:
            raise error.BadArgumentError(
                'No proto component specified at %s' % self.__class__
            )
        if not hasattr(self, '_componentCache'):
            self._componentCache = {}
        for uniqId in self._componentCache.keys():
            if self._componentCache[uniqId] is not None:
                c = self._componentCache[uniqId]
                self._componentCache[uniqId] = None
                return c
        c = self.protoComponent.clone()
        self._componentCache[id(c)] = None
        return c

    def componentFactoryReturn(self, *vals):
        if self.protoComponent is None:
            raise error.BadArgumentError(
                'No proto component specified at %s' % self.__class__
            )
        if not hasattr(self, '_componentCache'):
            self._componentCache = {}
        for val in vals:
            valId = id(val)
            if self._componentCache.has_key(valId):
                if self._componentCache[valId] is None:
                    self._componentCache[valId] = val
                else:
                    raise error.BadArgumentError(
                        'Extra component return %s' % val
                    )

    # Mutable sequence object protocol

    def __setitem__(self, idx, value):
        if type(idx) == SliceType:
            apply(self.componentFactoryReturn,
                  self._components[idx.start:idx.stop])            
            setslice(self._components, idx.start, idx.stop, list(value))
            return

        if not isinstance(value, Asn1Item) or \
               not self.protoComponent.isSubtype(value):
            raise error.BadArgumentError(
                'Unexpected component type %s at %s' %
                (value.__class__.__name__, self.__class__.__name__)
            )

        self.verifyConstraints(value)
        self.componentFactoryReturn(self._components[idx])        
        self._components[idx] = value

    def __getitem__(self, idx):
        if type(idx) == SliceType:
            return getslice(self._components, idx.start, idx.stop)
        return self._components[idx]

    def __delitem__(self, idx):
        if type(idx) == SliceType:
            apply(self.componentFactoryReturn,
                  self._components[idx.start:idx.stop])
            delslice(self._components, idx.start, idx.stop)
            return        
        self.componentFactoryReturn(self._components[idx])
        del self._components[idx]

    # They won't be defined if version is at least 2.0 final
    if version_info < (2, 0):
        def __getslice__(self, i, j):
            return self[max(0, i):max(0, j):]
        def __setslice__(self, i, j, seq):
            self[max(0, i):max(0, j):] = seq
        def __delslice__(self, i, j):
            del self[max(0, i):max(0, j):]
        
    def append(self, value):
        if not isinstance(value, Asn1Item) or \
               not self.protoComponent.isSubtype(value):
            raise error.BadArgumentError(
                'Unexpected component type %s at %s' %
                (value.__class__.__name__, self.__class__.__name__)
            )

        self.verifyConstraints(value)
        self._components.append(value)

    def extend(self, values):
        if TupleType != type(values) != ListType:
            raise error.BadArgumentError(
                'Non-list arg to %s.extend: %s' %
                (self.__class__.__name__, type(values))
            )
        for value in values:
            self.append(value)

    def insert(self, idx, value):
        if not isinstance(value, Asn1Item) or \
               not self.protoComponent.isSubtype(value):
            raise error.BadArgumentError(
                'Unexpected component type %s at %s' %
                (value.__class__.__name__, self.__class__.__name__)
            )

        self.verifyConstraints(value)
        self._components.insert(idx, value)
        
    def pop(self, idx=None):
        c = self._components.pop(idx)
        self.componentFactoryReturn(c)
        return c

    def index(self, idx): return self._components.index(idx)
    def __len__(self): return len(self._components)

    def clear(self):
        apply(self.componentFactoryReturn, self._components)
        self._components = []
