"""
   A framework for implementing ASN.1 data types.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'tagClasses', 'tagFormats', 'tagCategories', 'SimpleAsn1Object', \
            'RecordTypeAsn1Object', 'ChoiceTypeAsn1Object', \
            'VariableTypeAsn1Object' ]

from types import *
from pysnmp.asn1 import error

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

class Asn1Object:
    """Base class for all ASN.1 objects
    """
    #
    # ASN.1 tags
    #
    tagClass = tagClasses['UNIVERSAL']
    tagFormat = None
    tagId = None
    tagCategory = tagCategories['IMPLICIT']
    
    #
    # Argument type constraint
    #
    allowedTypes = []

    #
    # Subtyping stuff
    #

    # A list of permitted values
    singleValueConstraint = []

    # A list of classes representing contained subtypes
    containedSubtypeConstraint = []

    # A tuple of (min, max) of allowed value
    valueRangeConstraint = ()

    # A tuple of (min, max) of allowed size of value
    sizeConstraint = ()

    # A list of permitted character values
    permittedAlphabetConstraint = []

    # Hmm, crunchy so far
    innerSubtypeConstraint = {}

    # All constraints available by default
    _subtype_single_value_constraint = 1
    _subtype_contained_subtype_constraint = 1
    _subtype_value_range_constraint = 1
    _subtype_size_constraint = 1
    _subtype_permitted_alphabet_constraint = 1
    _subtype_inner_subtype_constraint = 1

    def _subtype_constraint(self, value):
        """All constraints checking method
        """
        # Single value constraint
        if len(self.singleValueConstraint):
            if self._subtype_single_value_constraint is None:
                raise error.ValueConstraintError('Single value constraint not applicible to %s' % self.__class__.__name__)
            if value not in self.singleValueConstraint:
                raise error.ValueConstraintError('Single value constraint for %s: %s not within allowed values' % (self.__class__.__name__, str(value)))

        # Contained subtype constraint
        if len(self.containedSubtypeConstraint):
            if self._subtype_contained_subtype_constraint is None:
                raise error.ValueConstraintError('Contained subtype constraint not applicible to %s' % self.__class__.__name__)
            for subType in self.containedSubtypeConstraint:
                # Attempt to instantiate contained subtype with our value
                subType(value)

        # Value range constraint
        if len(self.valueRangeConstraint):
            if self._subtype_value_range_constraint is None:
                raise error.ValueConstraintError('Value range constraint not applicible to %s' % self.__class__.__name__)
            if not (self.valueRangeConstraint[0] <= value <= \
                    self.valueRangeConstraint[1]):
                raise error.ValueConstraintError('Value range constraint for %s: %s not in %s' % (self.__class__.__name__, str(value), str(self.valueRangeConstraint)))

        # Size constraint
        if len(self.sizeConstraint):
            if self._subtype_size_constraint is None:
                raise error.ValueConstraintError('Value size constraint not applicible to %s' % self.__class__.__name__)
            if not (self.sizeConstraint[0] <= len(value) \
                    <= self.sizeConstraint[1]):
                raise error.ValueConstraintError('Value size constraint for %s: %s not in %s' % (self.__class__.__name__, str(value), str(self.sizeConstraint)))

        # Permitted alphabet constraint
        if len(self.permittedAlphabetConstraint):
            if self._permitted_alphabet_constraint is None:
                raise error.ValueConstraintError('Permitted alphabet constraint not applicible to %s' % self.__class__.__name__)
            if value not in self.permittedAlphabetConstraint:
                raise error.ValueConstraintError('Permitted alphabet constraint for %s: %s out of alphabet' % (self.__class__.__name__, str(value)))

        # Inner subtype constraint
        if len(self.innerSubtypeConstraint):
            if self._subtype_inner_subtype_constraint is None:
                raise error.ValueConstraintError('Inner subtype constraint not applicible to %s' % self.__class__.__name__)
            # XXX not implemented so far
                
    def _type_constraint(self, value):
        """
        """
        if len(self.allowedTypes):
            for allowedType in self.allowedTypes:
                if isinstance(value, allowedType):
                    break
            else:
                raise error.ValueConstraintError('Value type constraint for %s: %s not in %s' % (self.__class__.__name__, type(value), str(self.allowedTypes)))
        
    def getUnderlyingTag(self):
        """
        """
        for superClass in self.__class__.__bases__:
            if issubclass(self.__class__, superClass):
                break
        else:
            raise error.BadArgumentError('No underlying type for %s' % \
                                         self.__class__.__name__)

        return (superClass.tagClass, superClass.tagFormat, superClass.tagId)
    
class SimpleAsn1Object(Asn1Object):
    """Base class for a simple ASN.1 object. Defines behaviour and
       properties of various non-structured ASN.1 objects.
    """
    tagFormat = tagFormats['SIMPLE']
    tagId = 0x00
    initialValue = None

    # Disable not applicible constraints
    _subtype_inner_subtype_constraint = None
    
    def __init__(self, value=None):
        """Store ASN.1 value
        """
        self.set(value)

    def __str__(self):
        """Return string representation of class instance
        """
        return '%s: %s' % (self.__class__.__name__, str(self.get()))

    def __repr__(self):
        """Return native representation of instance payload
        """
        return self.__class__.__name__ + '(' + repr(self.get()) + ')'

    def __cmp__(self, other):
        """Attempt to compare the payload of instances of the same class
        """
        if hasattr(self, '_cmp'):
            return self._cmp(other)
        
        if type(other) == InstanceType and isinstance(other, SimpleAsn1Object):
            if not isinstance(other, self.__class__):
                other = self.__class__(other.get())
        else:
            other = self.__class__(other)

        return cmp(self.rawAsn1Value, other.rawAsn1Value)

    def __hash__(self):
        """Returns hash of the payload value
        """
        try:
            return hash(self.rawAsn1Value)

        except TypeError:
            # Attempt to hash sequence value
            return reduce(lambda x, y: x ^ y, map(hash, self.rawAsn1Value),
                          hash(None))

    def __nonzero__(self):
        """Returns true if value is true
        """
        if self.rawAsn1Value:
            return 1
        else:
            return 0

    def _setRawAsn1Value(self, value):
        if hasattr(self, '_subtype_constraint'):
            self._subtype_constraint(value)

        # Optionally copy a value
        valType = type(value)
        # Supported mutable type            
        if valType == ListType:
            # Copy mutable object
            self.rawAsn1Value = []; self.rawAsn1Value.extend(value)
        # Supported immutable types
        elif valType == IntType or \
             valType == LongType or \
             valType == StringType or \
             valType == NoneType or \
             valType == FloatType or \
             valType == TupleType:
            self.rawAsn1Value = value
        else:
            raise errorBadArgumentError('Unsupported value type to hold at %s: %s' % (self.__class__.__name__, valType))
        
    #
    # Simple ASN.1 object protocol definition
    #

    def set(self, value):
        """Set a value to object
        """
        if value is None:
            if self.initialValue is None:
                self.rawAsn1Value = None
                return
            else:
                if callable(self.initialValue):
                    self.initialValue()
                    return
                else:
                    value = self.initialValue

        # Allow initalization from instances of the same type
        if isinstance(value, self.__class__):
            self._setRawAsn1Value(value.rawAsn1Value)
            return
        
        if hasattr(self, '_type_constraint'):
            self._type_constraint(value)

        if hasattr(self, '_iconv'):
            value = self._iconv(value)

        self._setRawAsn1Value(value)
        
    def get(self):
        """Get a value from object
        """
        if hasattr(self, '_oconv'):
            return self._oconv(self.rawAsn1Value)
        
        return self.rawAsn1Value

    def getTerminal(self):
        # Already a terminal
        return self

class StructuredAsn1Object(Asn1Object):
    """Base class for structured ASN.1 objects
    """
    tagFormat = tagFormats['CONSTRUCTED']
    
    # Disable not applicible constraints
    _subtype_value_range_constraint = None
    _subtype_permitted_alphabet_constraint = None

    def getTerminal(self):
        raise error.BadArgumentError('Ambigious type %s for operation' % \
                                     (self.__class__.__name__))

class FixedTypeAsn1Object(StructuredAsn1Object):
    """Base class for fixed-type ASN.1 objects
    """
    # Disable not applicible constraints
    _subtype_size_constraint = None

    def __init__(self):
        """Initialize object internals
        """
        # Dictionary emulation (for strict ordering)
        self._names = []; self._components = []

    def __str__(self):
        """Return string representation of class instance
        """
        s = ''
        for idx in range(len(self)):
            if s:
                s = s + ', '
            s = s + '%s: %s' % (self._names[idx], str(self._components[idx]))
        return '%s: %s' % (self.__class__.__name__, s)

    def __repr__(self):
        """Return native representation of instance payload
        """
        s = ''
        for idx in range(len(self)):
            if s:
                s = s + ', '
            s = s + '%s=%s' % (self._names[idx], repr(self._components[idx]))
        return '%s(%s)' % (self.__class__.__name__, s)

    def __cmp__(self, other):
        """Attempt to compare the payload of instances of the same class
        """
        if hasattr(self, '_cmp'):
            return self._cmp(other)

        if type(other) != InstanceType or not \
           isinstance(other, self.__class__):
            raise error.BadArgumentError('Incompatible types for comparation %s with %s' % (self.__class__.__name__, str(other)))

        return cmp(self._names, other._names) | \
               cmp(self._components, other._components)

    def __hash__(self):
        """Returns hash of the payload value
        """
        return reduce(lambda x, y: x ^ y, map(hash, self._names) +
                      map(hash, self._components), hash(None))

    #
    # Mapping object protocol (re-implemented for strict ordering)
    #

    def __getitem__(self, key):
        """Return component by key
        """
        try:
            idx = self._names.index(key)

        except ValueError:
            raise KeyError, str(key)

        else:
            return self._components[idx]

    def keys(self):
        """Return a list of keys
        """
        return self._names

    def has_key(self, key):
        """Return true if key exists
        """
        try:
            self._names.index(key)

        except ValueError:
            return None

        return 1
    
    def values(self):
        """Return a list of values
        """
        return self._components

    def items(self):
        """Return a list of tuples (key, value)
        """
        return map(lambda x, y: (x, y), self._names, self._components)

    def update(self, dict):
        """Merge dict to ourselves
        """
        for key in dict.keys():
            self[key] = dict[key]

    def get(self, key, default=None):
        """Lookup by key with default
        """
        if self.has_key(key):
            return self[key]
        else:
            return default
        
    def __len__(self):
        """Return the number of components
        """
        return len(self._components)

class RecordTypeAsn1Object(FixedTypeAsn1Object):
    """Base class for fixed-structure ASN.1 objects
    """
    fixedNames = []; fixedComponents = []
    
    def __init__(self, **kwargs):
        """Store dictionary args
        """
        FixedTypeAsn1Object.__init__(self)

        # Initialize fixed structure
        self._names.extend(self.fixedNames)
        self._components = []
        for fixedComponent in self.fixedComponents:
            self._components.append(fixedComponent())

        self.update(kwargs)

    #
    # Mapping object protocol (re-implemented for strict ordering)
    #

    def __setitem__(self, key, value):
        """Set component by key & value
        """
        # Hard-coded type constraint XXX
        if not isinstance(value, Asn1Object):
            raise error.BadArgumentError('Non-ASN1 object %s at %s'\
                                         % (repr(value), \
                                            self.__class__.__name__))

        if hasattr(self, '_type_constraint'):
            self._type_constraint(value)

        if hasattr(self, '_subtype_constraint'):
            self._subtype_constraint(value)

        # XXX
        try:
            idx = self._names.index(key)

        except ValueError:
            raise error.BadArgumentError('No such identifier %s at %s' %\
                                         (key, self.__class__.__name__))

        else:
            if not isinstance(value, self._components[idx].__class__):
                raise error.BadArgumentError('Component type mismatch: %s vs %s' % (self._components[idx].__class__.__name__, value.__class__.__name__))
            self._components[idx] = value

class ChoiceTypeAsn1Object(FixedTypeAsn1Object):
    """Base class for choice-type ASN.1 objects
    """
    choiceNames = []; choiceComponents = []
    initialComponent = None
    
    def __init__(self, **kwargs):
        """Store dictionary args
        """
        FixedTypeAsn1Object.__init__(self)
        if len(kwargs) == 0 and self.initialComponent is not None:
            kwargs[''] = self.initialComponent()
        self.update(kwargs)

    def getTerminal(self):
        """Attempt to fetch and return terminal component recursively
        """
        if len(self.keys()) == 0:
            raise error.BadArgumentError('No initialized component at %s'\
                                         % (self.__class__.__name__))
        component = self.values()[0]
        if isinstance(component, ChoiceTypeAsn1Object):
            return component.getTerminal()
        return component

    #
    # Dictionary interface emulation (for strict ordering)
    #

    def __setitem__(self, key, value):
        """Set component by key & value
        """
        # Hard-coded type constraint XXX
        if not isinstance(value, Asn1Object):
            raise error.BadArgumentError('Non-ASN.1 assignment at %s: %s'\
                                         % (self.__class__.__name__,
                                            repr(value)))

        if hasattr(self, '_type_constraint'):
            self._type_constraint(value)

        if hasattr(self, '_subtype_constraint'):
            self._subtype_constraint(value)

        for choiceComponent in self.choiceComponents:
            if isinstance(value, choiceComponent):
                # Drop possibly existing values as it is a CHOICE
                self._components = [ value ]                
                idx = self.choiceComponents.index(choiceComponent)
                try:
                    self._names = [ self.choiceNames[idx] ]

                except IndexError:
                    self._names = [ str(choiceComponent.__name__) ]
                break
        else:
            raise error.BadArgumentError('Unexpected component type %s at %s'\
                                         % (value.__class__.__name__, \
                                            self.__class__.__name__))

    def __delitem__(self, key):
        """Delete component by key
        """
        try:
            idx = self._names.index(key)

        except ValueError:
            raise KeyError, str(key)

        else:
            del self._names[idx]
            del self._components[idx]

class AnyTypeAsn1Object(FixedTypeAsn1Object):
    """Base class for any-type ASN.1 objects
    """
    initialComponent = None
    
    def __init__(self, **kwargs):
        """Store dictionary args
        """
        FixedTypeAsn1Object.__init__(self)
        if len(kwargs) == 0 and self.initialComponent is not None:
            kwargs[''] = self.initialComponent()
        self.update(kwargs)

    #
    # Dictionary interface emulation (for strict ordering)
    #

    def __setitem__(self, key, value):
        """Set component by key & value
        """
        # Hard-coded type constraint XXX
        if not isinstance(value, Asn1Object):
            raise error.BadArgumentError('Non-ASN.1 assignment at %s: %s'\
                                         % (self.__class__.__name__,
                                            repr(value)))

        if hasattr(self, '_type_constraint'):
            self._type_constraint(value)

        if hasattr(self, '_subtype_constraint'):
            self._subtype_constraint(value)

        # Drop possibly existing values as it is of a CHOICE nature
        self._names = [ key ]
        self._components = [ value ]

    def __delitem__(self, key):
        """Delete component by key
        """
        try:
            idx = self._names.index(key)

        except ValueError:
            raise KeyError, str(key)

        else:
            del self._names[idx]
            del self._components[idx]

class VariableTypeAsn1Object(StructuredAsn1Object):
    """Base class for variable-structure ASN.1 objects
    """
    # The only carried type
    protoComponent = None

    # Initial arguments to 'protoComponent'
    initialValue = []
    
    def __init__(self, *args):
        """Store possible components
        """
        # List emulation
        self._components = []
        args = list(args)
        if len(args) == 0:
            for val in self.initialValue:
                args.append(val())
        self.extend(args)

    def __str__(self):
        """Return string representation of class instance
        """
        s = ''
        for idx in range(len(self)):
            if s:
                s = s + ', '
            s = s + '%s' % str(self._components[idx])
        return '%s: %s' % (self.__class__.__name__, s)

    def __repr__(self):
        """Return native representation of instance payload
        """
        s = ''
        for idx in range(len(self)):
            if s:
                s = s + ', '
            s = s + '%s' % repr(self._components[idx])
        return '%s(%s)' % (self.__class__.__name__, s)

    def __cmp__(self, other):
        """Attempt to compare the payload of instances of the same class
        """
        if hasattr(self, '_cmp'):
            return self._cmp(other)

        if type(other) != InstanceType or not \
           isinstance(other, self.__class__):
            raise error.BadArgumentError('Incompatible types for comparation %s with %s' % (self.__class__.__name__, str(other)))

        return cmp(self._components, other._components)

    def __hash__(self):
        """Returns hash of the payload value
        """
        return reduce(lambda x, y: x ^ y, map(hash, self._components),
                      hash(None))

    #
    # Mutable sequence object protocol
    #

    def __setitem__(self, idx, value):
        """Set object by subscription
        """
        # Hard-coded type constraint XXX
        if not isinstance(value, Asn1Object):
            raise error.BadArgumentError('Non-ASN1 object %s at %s'\
                                         % (repr(value), \
                                            self.__class__.__name__))

        if type(self.protoComponent) != ClassType or \
           not isinstance(value, self.protoComponent):
            raise error.BadArgumentError('Unexpected component type %s at %s'\
                                         % (value.__class__.__name__, \
                                            self.__class__.__name__))

        if hasattr(self, '_type_constraint'):
            self._type_constraint(value)

        if hasattr(self, '_subtype_constraint'):
            self._subtype_constraint(value)

        self._components[idx] = value

    def __getitem__(self, idx):
        """Get object by subscription
        """
        return self._components[idx]

    def __delitem__(self, idx):
        """Remove object by subscription
        """
        del self._components[idx]

    def append(self, value):
        """Append object to end
        """
        # Hard-coded type constraint XXX
        if not isinstance(value, Asn1Object):
            raise error.BadArgumentError('Non-ASN1 object %s at %s' %\
                                         (repr(value), \
                                          self.__class__.__name__))

        if type(self.protoComponent) != ClassType or \
           not isinstance(value, self.protoComponent):
            raise error.BadArgumentError('Unexpected component type %s at %s'\
                                         % (value.__class__.__name__, \
                                            self.__class__.__name__))

        if hasattr(self, '_type_constraint'):
            self._type_constraint(value)

        if hasattr(self, '_subtype_constraint'):
            self._subtype_constraint(value)

        self._components.append(value)

    def extend(self, values):
        """Extend list by appending list elements
        """
        if type(values) != ListType:
            raise error.BadArgumentError('Non-list arg to %s.extend: %s'\
                                         % (self.__class__.__name__,
                                            type(values)))
        for value in values:
            self.append(value)

    def insert(self, idx, value):
        """Insert object before index
        """
        # Hard-coded type constraint XXX
        if not isinstance(value, Asn1Object):
            raise error.BadArgumentError('Non-ASN1 object %s at %s' %\
                                         (repr(value),\
                                          self.__class__.__name__))

        if type(self.protoComponent) != ClassType or \
           not isinstance(value, self.protoComponent):
            raise error.BadArgumentError('Unexpected component type %s at %s'\
                                         % (value.__class__.__name__, \
                                            self.__class__.__name__))

        if hasattr(self, '_type_constraint'):
            self._type_constraint(value)

        if hasattr(self, '_subtype_constraint'):
            self._subtype_constraint(value)

        self._components.insert(idx, value)
        
    def pop(self, idx=None):
        """Remove and return item at index (default last)
        """
        self._components.pop(idx)

    def index(self, idx):
        """Return component index by value
        """
        return self._components.index(idx)
        
    def __len__(self):
        """
        """
        return len(self._components)
