"""An implementation of high-level API to SNMP data types (RFC1155)"""
from types import InstanceType
from pysnmp.asn1 import univ
from pysnmp.proto.omni import error
from pysnmp.asn1.error import BadArgumentError

class SequenceMixIn:
    def omniSetSimpleComponent(self, key, value):
        if type(value) == InstanceType:
            self[key] = value
        else:
            self[key].set(value)
        
class ChoiceMixIn:
    def omniGetCurrentComponent(self):
        if self:
            return self.values()[0]
        raise error.BadArgumentError(
            'No initialized component at %s' % self.__class__.__name__
        )

    def omniGetTerminalValue(self):
        if self:        
            component = self.values()[0]
            f = getattr(component, 'omniGetTerminalValue', None)
            if f is not None: return f()
            return component
        raise error.BadArgumentError(
            'No initialized value at %s' % self.__class__.__name__
        )

    # XXX left for compatibility
    getTerminal = omniGetTerminalValue

    def omniSetTerminalValue(self, value):
        keys = self.keys() + self.protoComponents.keys()
        # At first, try upper level
        for key in keys:
            if self.protoComponents[key].isSubtype(value):
                try:
                    self[key] = value
                    return
                except BadArgumentError:
                    pass
        # Otherwise, try inner components where available
        for key in keys:
            if hasattr(self.protoComponents[key], 'omniSetTerminalValue'):
                comp = self.componentFactoryBorrow(key)
                try:
                    comp.omniSetTerminalValue(value)
                except error.BadArgumentError:
                    continue
                self[key] = comp
                break
        else:
            raise error.BadArgumentError(
                'Unapplicable component %s at %s' %
                (value, self.__class__.__name__)
            )

mixInComps = [ (univ.Sequence, SequenceMixIn),               
               (univ.Choice, ChoiceMixIn) ]

for (baseClass, mixIn) in mixInComps:
    if mixIn not in baseClass.__bases__:
        baseClass.__bases__ = (mixIn, ) + baseClass.__bases__
