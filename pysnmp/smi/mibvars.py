"""MIB objects interface"""
from bisect import bisect
from pysnmp.asn1.base import Asn1Item
from pysnmp.smi.indices import OidOrderedDict
from pysnmp.smi import error

class AbstractMibVariable:
    initialName = None
    def __init__(self, name=None):
        if name:
            self.name = name
        else:
            self.name = self.initialName
            
    def handleRead(self, name, var):
        raise error.NotImplementedError(
            'Variable read not implemented at %s' % self
            )
    def handleWrite(self, name, var):
        raise error.NotImplementedError(
            'Variable write not implemented at %s' % self
            )
    
class MibVariables:
    def __init__(self, mib=None):
        self.__mib = mib
        self.__vars = OidOrderedDict()

    def registerVariables(self, *mibVars):
        for mibVar in mibVars:
            if self.__mib:
                oid, label = self.__mib.getOidLabel(mibVar.name)
            else:
                oid = mibVar.name
            if self.__vars.has_key(oid):
                raise error.BadArgumentError(
                    'Duplicate OID encountered %s' % oid
                    )
            self.__vars[oid] = mibVar

    def unregisterVariables(self, *mibVars):
        for mibVar in mibVars:
            if self.__mib:
                oid, label = self.__mib.getOidLabel(mibVar.name)
            else:
                oid = mibVar.name            
            if self.__vars.has_key(oid):
                del self.__vars[oid]

    def readVariable(self, name, val=None):
        mibVar = self.__vars.get(name)
        if mibVar is None:
            raise error.NoSuchInstance(
                'No variable associated with %s at the MIB' % name
                )
        val = mibVar.handleRead(name, val)
        if isinstance(val, Asn1Item):
            return val
        mibNode = self.__mib.getNode(name)
        if mibNode:
            return mibNode.getSyntax(self.__mib).set(val)
        raise error.NoSuchInstance(
            'No MIB information for OID %s' % name
            )
    
    def readNextVariable(self, name, val=None):
        names = self.__vars.keys()
        if self.__vars.has_key(name):
            nextIdx = names.index(name) + 1
        else:
            nextIdx = bisect(names, name)
        while nextIdx < len(names):
            return self.readVariable(names[nextIdx], val)

    def writeVariable(self, name, val):
        mibVar = self.__vars.get(name)
        if mibVar is None:
            raise error.NoSuchInstance(
                'No variable associated with %s at the MIB' % name
                )
        val = mibVar.handleWrite(name, val)
        if isinstance(val, Asn1Item):
            return val
        mibNode = self.__mib.getNode(name)
        if mibNode:
            return mibNode.getSyntax(self.__mib).set(val)
        raise error.NoSuchInstance(
            'No MIB information for OID %s' % name
            )

if __name__ == '__main__':
    from pysnmp.smi.node import MibType

    class SysDescrMibVariable(AbstractMibVariable):
        initialName = 'sysDescr'
        def handleRead(self, name, val=None):
            return 'mysys'
            
    mv = MibVariables()
    mv.registerVariables(SysDescrMibVariable())
    print mv.readVariable('.1.3.6.1.2.1.1.1')
