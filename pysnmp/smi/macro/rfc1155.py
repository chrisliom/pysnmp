"""RFC1155 SMI macros implementations"""
from string import join

class AbstractNode:
    value = label = None

    def __init__(self, **kwargs):
        self.value = kwargs.get('value')
        self.label = kwargs.get('label')
        
    def __str__(self):
        return '{ %s %s }' % (self.label, self.value)
    
class ObjectType(AbstractNode):
    syntax = access = status = module = None

    def __init__(self, **kwargs):
        apply(AbstractNode.__init__, [self], kwargs)
        self.syntax = kwargs.get('syntax')
        self.access = kwargs.get('access')
        self.status = kwargs.get('status')
        self.module = kwargs.get('module')
        
    def __str__(self):
        r = [ '%s OBJECT-TYPE' % self.label ]
        if self.syntax:
            r.append('SYNTAX %s' % self.syntax)
        if self.access:
            r.append('ACCESS %s' % self.access)
        if self.status:
            r.append('STATUS %s' % self.status)
        if self.value:
            r.append(' = { %s }' % self.value)
        return join(r, '\n')
