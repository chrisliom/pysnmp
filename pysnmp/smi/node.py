"""MIB nodes interfaces"""
from string import join, split
from pysnmp.smi.indices import OrderedDict
from pysnmp.smi import error
from pysnmp.asn1 import subtypes

class MibEntry(OrderedDict):
    def __init__(self, **kwargs):
        apply(OrderedDict.__init__, [self], kwargs)
        if self.get('module') is None:
            self['module'] = '<builtin>'
    
class MibType(MibEntry):
    def inputFilter(self, value):
        if value is not None:
            enum = self.get('singleValueConstraint')
            if enum:
                for lab, val in enum:
                    if lab == value:
                        value = val
                        break
        return value
        
    def getSyntax(self, mibTree, initialValue=None):
        """Resolve type spec into ASN1 type instance"""
        syntax = self.get('syntax')
        if syntax is not None:
            if initialValue is None:
                return syntax.clone()
            else:
                # Terminal type
                return syntax.clone().set(self.inputFilter(initialValue))

        # Lookup base type
        baseTypeNode = mibTree.getType(self.get('baseName'),
                                       self.get('baseMod'))
        if not baseTypeNode:
            raise error.BadArgumentError(
                'Base type %s:%s is missing at %r' % \
                (self.get('name'), self.get('module'), self)
                )        
        syntax = baseTypeNode.getSyntax(mibTree)
        if syntax is None:
            return

        # Apply range constraints to base type
        range = self.get('rangeConstraint')
        if range:
            syntax.subtypeConstraints = syntax.subtypeConstraints + (
                subtypes.ValueRangeConstraint(range[0], range[1]),
                )

        # Apply single-value contstaints
        enum = self.get('singleValueConstraint')
        if enum:
            syntax.subtypeConstraints = syntax.subtypeConstraints + (
                apply(subtypes.SingleValueConstraint,
                      map(lambda (l, v): v, enum)),
                )

        if initialValue is not None:
            syntax.set(self.inputFilter(initialValue))            
        return syntax
        
    def outputFilter(self, mibTree, value=None):
        syntax = self.getSyntax(mibTree)
        if value is not None: syntax.set(value)
        enum = self.get('singleValueConstraint')
        if enum:
            v = syntax.get()
            for lab, val in enum:
                if val == v:
                    return '%s(%s)' % (lab, val)
        return '%s' % syntax.get()

    def strSmiEntry(self): return self.get('name')

    def strTypeName(self):
        t = self.get('name')
        if t: return t
        return self.get('baseName')
        
class MibNode(MibEntry):
    def strSmiEntry(self):
        return '{ %s %s }' % (self.get('name'), self.get('value'))

    def strNodeName(self, mibTree):
        oid, label, suffix = mibTree.getOidLabel(self.get('value'))
        modName = self.get('module')
        if not modName:
            return label
        return modName+'::'+join(split(label, '.')[-1:], '.')
        
    def getSyntax(self):
        syntax = self.get('syntax')
        if not syntax:
            raise error.MibError(
                'Missing type notation at %s' % self
                )
        return syntax
