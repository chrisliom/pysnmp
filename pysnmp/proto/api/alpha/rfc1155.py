"""An implementation of high-level API to SNMP data types (RFC1155)"""
from types import InstanceType
from pysnmp.proto import rfc1155
from pysnmp.proto.api import error
from pysnmp.asn1.error import BadArgumentError

class SequenceMixIn:
    def apiAlphaSetSimpleComponent(self, key, value):
        if type(value) == InstanceType:
            self[key] = value
        else:
            self[key].set(value)
        
class ChoiceMixIn:
    def apiAlphaGetCurrentComponent(self):
        if self:
            return self.values()[0]
        raise error.BadArgumentError(
            'No initialized component at %s' % self.__class__.__name__
        )

    def apiAlphaGetTerminalValue(self):
        if self:        
            component = self.values()[0]
            f = getattr(component, 'apiAlphaGetTerminalValue', None)
            if f is not None: return f()
            return component
        raise error.BadArgumentError(
            'No initialized value at %s' % self.__class__.__name__
        )

    # XXX left for compatibility
    getTerminal = apiAlphaGetTerminalValue

    def apiAlphaSetTerminalValue(self, value):
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
            if hasattr(self.protoComponents[key], 'apiAlphaSetTerminalValue'):
                comp = self.componentFactoryBorrow(key)
                try:
                    comp.apiAlphaSetTerminalValue(value)
                except error.BadArgumentError:
                    continue
                self[key] = comp
                break
        else:
            raise error.BadArgumentError(
                'Unapplicable component %s at %s' %
                (value, self.__class__.__name__)
            )

mixInComps = [ (rfc1155.Sequence, SequenceMixIn),               
               (rfc1155.Choice, ChoiceMixIn) ]

for (baseClass, mixIn) in mixInComps:
    if mixIn not in baseClass.__bases__:
        baseClass.__bases__ = (mixIn, ) + baseClass.__bases__
