from string import split, join
from pysnmp.asn1 import univ, subtypes
from pysnmp.smi import error

# base ASN.1 objects with SNMP table indexing & pretty print facilities support

class Integer(univ.Integer):
    def setFromName(self, value, impliedFlag=None):
        self.set(value[0])
        return value[1:]
    
    def getAsName(self, impliedFlag=None):
        return (self.get())

class OctetString(univ.OctetString):
    def setFromName(self, value, impliedFlag=None):
        if impliedFlag:
            s = reduce(lambda x,y: x+y, map(lambda x: chr(x), value))
        else:
            s = reduce(lambda x,y: x+y, map(lambda x: chr(x), value[1:]))
            # XXX check name vs str length
        valueLength = len(s)
        while valueLength:
            try:
                self.set(s[:valueLength])
                s = s[valueLength:]
                # XXX
                if impliedFlag:
                    initial = ()
                else:
                    initial = (len(self),)
                return reduce(
                    lambda x,y: x+(y,), map(lambda x: ord(x), s), initial
                    )
            except subtypes.ValueConstraintError:
                valueLength = valueLength - 1
            raise error.SmiError(
                'Instance ID %s does not fit INDEX %r' % (value, self)
                )
    
    def getAsName(self, impliedFlag=None):
        if impliedFlag:
            initial = ()
        else:
            initial = (len(self),)
        return reduce(
            lambda x,y: x+(y,), map(lambda x: ord(x), self), initial
            )

BitString = univ.BitString
Null = univ.Null

class ObjectIdentifier(univ.ObjectIdentifier):
    def setFromName(self, value, impliedFlag=None):
        if impliedFlag:
            self.set(value)
        else:
            self.set(value[1:])
        return ()

    def getAsName(self, impliedFlag=None):
        if impliedFlag:
            return tuple(self)
        else:
            return (len(self),) + tuple(self)

mibBuilder.exportSymbols(
    modName, Integer=Integer, OctetString=OctetString,
    BitString=BitString, Null=Null, ObjectIdentifier=ObjectIdentifier
    )
