"""
   A framework for implementing ASN.1 data types. Fundamental and
   non-structured SNMP-specific objects included.

   Written by Ilya Etingof <ilya@glas.net>, 1999-2002.
"""
# Module public names
__all__ = [ 'SimpleAsn1Object', 'StructuredAsn1Object' ]

from types import InstanceType
import error

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

class Asn1Object:
    """Base class for all ASN.1 object.
    """
    #
    # ASN.1 tags
    #
    tagClass = tagClasses['UNIVERSAL']
    tagFormat = None
    tagId = None
    tagCategory = 'IMPLICIT'
    
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

    def _subtype_single_value_constraint(self, value):
        """Particular subtype constraint checking method
        """
        if self.singleValueConstraint:
            if value not in self.singleValueConstraint:
                raise error.BadArgumentError('Single value constraint for %s: %s not within allowed values' % (self.__class__.__name__, str(value)))

    def _subtype_single_value_constraint_na(self, value):
        """
        """
        if self.singleValueConstraint:
            raise error.BadArgumentError('Single value constraint not applicible to %s' % self.__class__.__name__)

    def _subtype_contained_subtype_constraint(self, value):
        """Particular subtype constraint checking method
        """
        if self.containedSubtypeConstraint:
            for subType in self.containedSubtypeConstraint:
                # Attempt to instantiate contained subtype with our value
                subType(value)

    def _subtype_contained_subtype_constraint_na(self, value):
        """
        """
        if self.containedSubtypeConstraint:
            raise error.BadArgumentError('Contained subtype constraint not applicible to %s' % self.__class__.__name__)

    def _subtype_value_range_constraint(self, value):
        """Particular subtype constraint checking method
        """
        if self.valueRangeConstraint:
            if value < self.valueRangeConstraint[0] or \
               value > self.valueRangeConstraint[1]:
                raise error.BadArgumentError('Value range constraint for %s: %s not in %s' % (self.__class__.__name__, str(value), str(self.valueRangeConstraint)))

    def _subtype_value_range_constraint_na(self, value):
        """
        """
        if self.valueRangeConstraint:
            raise error.BadArgumentError('Value range constraint not applicible to %s' % self.__class__.__name__)

    def _subtype_size_constraint(self, value):
        """Particular subtype constraint checking method
        """
        if self.sizeConstraint:
            if len(value) < self.sizeConstraint[0] or \
               len(value) > self.sizeConstraint[1]:
                raise error.BadArgumentError('Value size constraint for %s: %s not in %s' % (self.__class__.__name__, str(value), str(self.sizeConstraint)))

    def _subtype_size_constraint_na(self, value):
        """
        """
        if self.sizeConstraint:
            raise error.BadArgumentError('Size constraint not applicible to %s' % self.__class__.__name__)

    def _subtype_permitted_alphabet_constraint(self, value):
        """Particular subtype constraint checking method
        """
        if self.permittedAlphabetConstraint:
            if value not in self.permittedAlphabetConstraint:
                raise error.BadArgumentError('Permitted alphabet constraint for %s: %s out of alphabet' % (self.__class__.__name__, str(value)))

    def _subtype_permitted_alphabet_constraint_na(self, value):
        """
        """
        if self.permittedAlphabetConstraint:
            raise error.BadArgumentError('Permitted alphabet constraint not applicible to %s' % self.__class__.__name__)

    def _subtype_inner_subtype_constraint(self, value):
        """Particular subtype constraint checking method XXX
        """
        pass

    def _subtype_inner_subtype_constraint_na(self, value):
        """
        """
        if self.innerSubtypeConstraint:
            raise error.BadArgumentError('Inner subtype constraint not applicible to %s' % self.__class__.__name__)

    def _subtype_constraint(self, value):
        """All constraints checking method
        """
        self._subtype_single_value_constraint(value)
        self._subtype_contained_subtype_constraint(value)
        self._subtype_value_range_constraint(value)
        self._subtype_size_constraint(value)
        self._subtype_permitted_alphabet_constraint(value)
        self._subtype_inner_subtype_constraint(value)
        
    def _type_constraint(self, value):
        """
        """
        if self.allowedTypes and type(value) not in self.allowedTypes:
            raise error.BadArgumentError('Value type constraint for %s: %s not in %s' % (self.__class__.__name__, type(value), str(self.allowedTypes)))

    def get_underling_tag(self):
        """
        """
        for superClass in self.__class__.__bases__:
            if issubclass(self.__class__, superClass):
                break
        else:
            raise error.BadArgumentError('No underling type for %s' % self.__class__.__name__)

        return (superClass.tagClass, superClass.tagFormat, superClass.tagId)
    
class SimpleAsn1Object(Asn1Object):
    """Base class for a simple ASN.1 object. Defines behaviour and
       properties of various non-structured ASN.1 objects.
    """
    tagFormat = tagFormats['SIMPLE']
    tagId = 0x00
    initialValue = None

    # Disable not applicible constraints
    _subtype_inner_subtype_constraint = Asn1Object._subtype_inner_subtype_constraint_na    
    
    def __init__(self, value=None):
        """Store ASN.1 value
        """
        self.set(value)

    def __str__(self):
        """Return string representation of class instance
        """
        if self.value == self.initialValue:
            return '%s: %s' % (self.__class__.__name__, str(self.value))
        else:
            return '%s: %s' % (self.__class__.__name__, str(self.get()))

    def __repr__(self):
        """Return native representation of instance payload
        """
        if self.value == self.initialValue:
            return self.__class__.__name__ + '()'
        else:
            return self.__class__.__name__ + '(' + repr(self.get()) + ')'

    def __cmp__(self, other):
        """Attempt to compare the payload of instances of the same class
        """
        if type(other) == InstanceType:
            if not isinstance(other, SimpleAsn1Object):
                raise errorBadArgument('Incompatible types for comparation %s with %s' % (self.__class__.__name__, str(other)))
            other = self.__class__(other.get())
        else:
            other = self.__class__(other)
        if hasattr(self, '_cmp'):
            return self._cmp(other)
        else:
            return cmp(self.value, other.value)
        
    #
    # Simple ASN.1 object protocol definition
    #
    
    def set(self, value):
        """Set a value to object
        """
        if value is None:
            self.value = self.initialValue
            return

        if hasattr(self, '_iconv'):
            value = self._iconv(value)
        
        if hasattr(self, '_type_constraint'):
            self._type_constraint(value)

        if hasattr(self, '_subtype_constraint'):
            self._subtype_constraint(value)

        self.value = value

    def get(self):
        """Get a value from object
        """
        if hasattr(self, '_oconv'):
            return self._oconv(self.value)
        
        return self.value

    def _setraw(self, value):
        """Set a raw value (skipping convertion and range chacking) to object
        """
        self.value = value

    def _getraw(self):
        """Get a raw value (skipping convertion and range chacking)
           from object
        """   
        return self.value

class StructuredAsn1Object(Asn1Object):
    """Base class for structured ASN.1 objects
    """
    tagFormat = tagFormats['CONSTRUCTED']
    initialNames = []
    initialComponents = []
    
    # Disable not applicible constraints
    _subtype_value_range_constraint = Asn1Object._subtype_value_range_constraint_na
    _subtype_permitted_alphabet_constraint = Asn1Object._subtype_permitted_alphabet_constraint_na

    def __init__(self, **kwargs):
        """Store dictionary args
        """
        # Dictionary emulation (for strict ordering)
        self._names = []; self._names.extend(self.initialNames)
        self._components = []; self._components.extend(self.initialComponents)

        # Wnen true, preserve object structure
        self.freezeStructure = None

        self.update(kwargs)

    def __str__(self):
        """Return string representation of class instance
        """
        s = '%s:' % self.__class__.__name__
        for idx in range(len(self)):
            s = s + ' %s: %s' % (self._names[idx], str(self._components[idx]))
        return s

    def __repr__(self):
        """Return native representation of instance payload
        """
        s = ''
        for idx in range(len(self)):
            if s:
                s = s + ', '
            s = s + '%s=%s' % (self._names[idx], str(self._components[idx]))
        return '%s(%s)' % (self.__class__.__name__, s)

    def __cmp__(self, other):
        """Attempt to compare the payload of instances of the same class
        """
        if type(other) == InstanceType:
            if not isinstance(other, StructuredAsn1Object):
                raise errorBadArgument('Incompatible types for comparation %s with %s' % (self.__class__.__name__, str(other)))
            other = self.__class__(other.get())
        else:
            other = self.__class__(other)

        if hasattr(self, '_cmp'):
            return self._cmp(other)

        return cmp(self.keys(), other.keys()) | \
                   cmp(self.values(), other.values())

    #
    # Dictionary interface emulation (for strict ordering)
    #

    def __setitem__(self, key, value):
        """
        """
        if not isinstance(value, Asn1Object):
            raise error.BadArgumentError('Not an ASN.1 object')

        try:
            idx = self._names.index(key)

        except ValueError:
            if self.freezeStructure:
                raise error.BadArgumentError('Object structure violation (no such identifier): %s' % key)
            self._names.append(key)
            self._components.append(value)

        else:
            if self._components[idx].__class__.__name__ != \
               value.__class__.__name__:
                raise error.BadArgumentError('Object structure violation (component type mismatch): %s vs %s' % (self._components[idx].__class__.__name__, value.__class__.__name__))
            self._components[idx] = value

    def __getitem__(self, key):
        """
        """
        try:
            idx = self._names.index(key)

        except ValueError:
            raise error.BadArgumentError(str(key))

        else:
            return self._components[self._names.index(key)]

    def keys(self):
        """
        """
        return self._names

    def has_key(self, key):
        """
        """
        try:
            return self._names.index(key)

        except ValueError:
            return None

    def values(self):
        """
        """
        return self._components

    def update(self, dict):
        """
        """
        for key in dict.keys():
            self[key] = dict[key]

    def __len__(self):
        """
        """
        return len(self._names)
