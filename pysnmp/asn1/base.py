"""A framework for implementing ASN.1 data types"""
try:
    from sys import version_info
except ImportError:
    version_info = ( 0, 0 )   # a really early version
version_info_major, version_info_minor = version_info[:2]
from operator import getslice, setslice, delslice
from string import join
from types import *
from pysnmp.asn1 import subtypes, error

# ASN.1 tagging

tagClasses = { 
    'UNIVERSAL'          : 0x00,
    'APPLICATION'        : 0x40,
    'CONTEXT'            : 0x80,
    'PRIVATE'            : 0xC0
    }

tagFormats = {
    'SIMPLE'             : 0x00,
    'CONSTRUCTED'        : 0x20
    }

tagCategories = {
    'IMPLICIT'           : 0x01,
    'EXPLICIT'           : 0x02,
    'UNTAGGED'           : 0x04
    }

class Asn1Item: pass

class Asn1ItemBase(Asn1Item):
    # ASN.1 tags
    tagClass = (tagClasses['UNIVERSAL'], )
    tagFormat = ()
    tagId = ()
    tagCategory = tagCategories['IMPLICIT']
    
    # Initializer type constraint
    allowedTypes = ()

    # A list of subtypes.Constraint instances for checking values
    subtypeConstraints = ()

    def _buildExplicitTags(self):
        # EXPLICIT stands for "in addition to" when it comes to tagging
        # Walk over base classes from top to bottom, build a sequence of
        # tags used for explicit tagging
        def walkOverBases(bases, tagCategory):            
            for baseClass in bases:
                if tagCategory != tagCategories['EXPLICIT']:
                    continue
                if type(baseClass) == TupleType:
                    # Multiple inheritance encountered
                    walkOverBases(baseClass, baseClass.tagCategory)
                else:
                    if not issubclass(baseClass, Asn1Item):
                        continue
                    # Make sure to skip duplicate class attrs
                    tagClassId = id(baseClass.tagClass)
                    tagFormatId = id(baseClass.tagFormat)
                    tagIdId = id(baseClass.tagId)
                    if seenTagClass.has_key(tagClassId) and \
                       seenTagFormat.has_key(tagFormatId) and \
                       seenTagId.has_key(tagIdId):
                        continue
                    seenTagClass[tagClassId] = seenTagFormat[tagFormatId] = \
                                               seenTagId[tagIdId] = 1
                    # Inherit tags
                    self.tagClass = self.tagClass + baseClass.tagClass
                    self.tagFormat = self.tagFormat + baseClass.tagFormat
                    self.tagId = self.tagId + baseClass.tagId

                    # Ascend upto bases
                    walkOverBases(baseClass.__bases__, baseClass.tagCategory)

        seenTagClass = {}; seenTagFormat = {}; seenTagId = {}
        walkOverBases(self.__class__.__bases__, self.__class__.tagCategory)

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
        if isinstance(other, Asn1ItemBase) and \
           self.tagId == other.tagId and \
           self.tagFormat == other.tagFormat and \
           self.tagClass == other.tagClass and \
           self.tagCategory == other.tagCategory:
            for c in other.subtypeConstraints:
                if c not in self.subtypeConstraints:
                    return
            return 1

    def clone(self):
        """Returns a new instance of this class with ASN1 subtype-sensitive
           attributes inherited from this class instance
        """   
        c = self.__class__()

        # Inherit tags
        c.tagClass = self.tagClass
        c.tagFormat = self.tagFormat
        c.tagId = self.tagId
        c.tagCategory = self.tagCategory

        # Inherit types
        c.allowedTypes = self.allowedTypes

        # Inherit subtypes
        c.subtypeConstraints = self.subtypeConstraints

        return c

# Base class for a simple ASN.1 object. Defines behaviour and
# properties of various non-structured ASN.1 objects.        
class AbstractSimpleAsn1Item(Asn1ItemBase):
    tagFormat = (tagFormats['SIMPLE'], )
    tagId = (0x00, )
    initialValue = None # no constraints checks
    
    def __init__(self, value=None):
        if self.tagCategory == tagCategories['EXPLICIT']:
            self._buildExplicitTags()
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
                other = self.componentFactoryBorrow(other.get())
        else:
            other = self.componentFactoryBorrow(other)
        return cmp(self.rawAsn1Value, other.rawAsn1Value)

    def __hash__(self):
        return hash((self.rawAsn1Value, self.tagClass, self.tagFormat,
                     self.tagId, self.tagCategory))

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
    tagFormat = (tagFormats['CONSTRUCTED'], )

class AbstractMappingAsn1Item(StructuredAsn1ItemBase):
    allowedTypes = ( Asn1Item, )

    def __init__(self):
        if self.tagCategory == tagCategories['EXPLICIT']:
            self._buildExplicitTags()
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
        if type(other) != InstanceType or not \
           isinstance(other, AbstractMappingAsn1Item):
            raise error.BadArgumentError(
                'Incompatible types for comparation %s with %s' %
                (self.__class__.__name__, str(other))
            )
        return cmp(self.items(), other.items())

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
        if self.tagCategory == tagCategories['EXPLICIT']:
            self._buildExplicitTags()
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
        if type(other) != InstanceType or not \
           isinstance(other, AbstractSequenceAsn1Item):
            raise error.BadArgumentError(
                'Incompatible types for comparation %s with %s' %
                (self.__class__.__name__, str(other))
            )
        return cmp(self._components, other._components)

    def componentFactoryBorrow(self):
        if self.protoComponent is None:
            raise error.BadArgumentError(
                'No proto component specified at %r' % self.__class__
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
                'No proto component specified at %r' % self.__class__
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
