"""
   ASN.1 subtype constraints classes.

   Constraints are relatively rare, but every ASN1 object
   is doing checks all the time for whether they have any
   constraints and whether they are applicable to the object.

   What we're going to do is define objects/functions that
   can be called unconditionally if they are present, and that
   are simply not present if there are no constraints.

   Original concept and code by Mike C. Fletcher.
"""
from types import StringType
from string import join
from pysnmp.asn1 import error

__all__ = [ 'SingleValueConstraint', 'ContainedSubtypeConstraint',
            'ValueRangeConstraint', 'ValueSizeConstraint',
            'PermittedAlphabetConstraint' ]

class ConstraintBase:
    """Abstract base-class for constraint objects

       Constraints should be stored in a simple sequence in the
       namespace of their client Asn1Object sub-classes.
    """
    def __init__(self, *values):
        """Initialise the constraint with items
           *values -- hashable objects allowed
        """ 
        v = {}
        for s in values: v[s] = 1
        self.values = v

    def __call__(self, client, value):
        """Raise errors if value not appropriate for client"""

    def __cmp__(self, other):
        if not isinstance(other, ConstraintBase):
            raise error.BadArgumentError(
                'Can only compare constraints'
                )
        return cmp(self.values, other.values)
    
class SingleValueConstraint(ConstraintBase):
    """Value must be part of defined values constraint"""
    def __call__(self, client, value):
        """Raise errors if value not appropriate for client"""
        if self.values.get(value) is None:
            raise error.ValueConstraintError(
                '%s for %s: value %s not within allowed values: %s' % (
                    self.__class__.__name__,
                    client.__class__.__name__,
                    str(value),
                    self.values.keys(),
                )
            )

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            join(map(lambda x: str(x), self.values.keys()), ', ')
        )
    
class ContainedSubtypeConstraint(ConstraintBase):
    """Value must satisfy all of defined set of constraints"""
    def __call__(self, client, value):
        """Raise errors if value not appropriate for client"""
        try:
            for c in self.values.keys():
                c(client, value)
        except error.ValueConstraintError, why:
            raise error.ValueConstraintError(
                'at %s %s' % (self.__class__.__name__, why)
            )

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            join(map(lambda x: str(x), self.values.keys()), ', ')
        )

class ValueRangeConstraint(ConstraintBase):
    """Value must be within start and stop values (inclusive)"""
    def __init__(self, start, stop):
        """Initialise the SingleValueConstraint with items

           start -- value below which errors are raised
           stop -- value above which errors are raised
        """
        if start > stop:
            raise error.BadArgumentError(
                '%s: screwed constraint values (start > stop): %s > %s' % (
                    self.__class__.__name__,
                    start, stop
                )
            )
        self.start, self.stop = start, stop
        # XXX
        apply(ConstraintBase.__init__, [self, start, stop])
        
    def __call__(self, client, value):
        """Raise errors if value not appropriate for client"""
        if type(value) == StringType:
            valLen = len(value)
        else:
            valLen = value
        if valLen < self.start or valLen > self.stop:
            raise error.ValueConstraintError(
                '%s for %s: value %s not within allowed range: %s through %s'%(
                    self.__class__.__name__,
                    client.__class__.__name__,
                    str(value),
                    self.start,
                    self.stop,
                )
            )

    def __repr__(self):
        return '%s(%d, %d)' % (
            self.__class__.__name__,
            self.start,
            self.stop
        )

class ValueSizeConstraint(ValueRangeConstraint):
    """len(value) must be within start and stop values (inclusive)"""
    def __call__(self, client, value):
        """Raise errors if value not appropriate for client"""
        length = len(value)
        if length < self.start or length > self.stop:
            raise error.ValueConstraintError(
                '%s for %s: len(value) %s (%s) not within allowed range: %s through %s' % (
                    self.__class__.__name__,
                    client.__class__.__name__,
                    str(value),
                    length,
                    self.start,
                    self.stop,
                )
            )

class PermittedAlphabetConstraint(SingleValueConstraint): pass

# class InnerSubtypeConstraint(ConstraintBase):
#     """Key value must be part of defined values constraint"""
#     def __init__(self, *keys):
#         """Initialise the InnerSubtypeConstraint with keys

#            *keys -- a set of tuples (key, <presence-flag>)
#         """
#         if version_info < (2, 2):
#             v = {}
#             for k, f in keys: v[k] = f
#             self.keys = v
#         else:
#             self.keys = dict([(k,f) for k, f in keys])
            
#     def __call__(self, client, value):
#         """Raise errors if value not appropriate for client"""
#         if self.values.get(value) is None:
#             raise error.ValueConstraintError(
#                 '%s for %s: value %s not within allowed values: %s' % (
#                     self.__class__.__name__,
#                     client.__class__.__name__,
#                     str(value),
#                     self.values.keys(),
#                 )
#             )
