# MIB modules loader
import os
from pysnmp.smi import error
try:
    import pysnmp_mibs
except ImportError:
    pysnmp_mibs = None

class MibBuilder:
    def __init__(self):
        self.lastBuildId = 0L
        paths = (os.path.join(os.path.split(error.__file__)[0], 'mibs'),)
        if os.environ.has_key('PYSNMP_MIB_DIR'):
            paths = paths + (
                os.path.join(os.path.split(os.environ['PYSNMP_MIB_DIR'])[0]),
                )
        if pysnmp_mibs:
            paths = paths + (
                os.path.join(os.path.split(pysnmp_mibs.__file__)[0]),
                )
        apply(self.setMibPath, paths)
        self.mibSymbols = {}

    # MIB modules management
    
    def setMibPath(self, *mibPaths):
        self.__mibPaths = map(os.path.normpath, mibPaths)

    def getMibPath(self): return tuple(self.__mibPaths)
        
    def loadModules(self, *modNames):
        # Build a list of available modules
        if not modNames:
            modNames = {}
            for mibPath in self.__mibPaths:
                try:
                    for modName in os.listdir(mibPath):
                        if modName[0] == '_' or modName[-3:] != '.py':
                            continue
                        modNames[modName[:-3]] = None
                except OSError:
                    continue
            modNames = modNames.keys()
        if not modNames:
            raise error.SmiError(
                'No MIB module to load at %s' % (self,)
                )
        for modName in modNames:
            if self.mibSymbols.has_key(modName):
                continue
            for mibPath in self.__mibPaths:
                modPath = os.path.join(
                    mibPath, modName + '.py'
                    )
                try:
                    open(modPath).close()
                except IOError, why:
                    continue
                break
            else:
                raise error.SmiError(
                    'MIB module %s open error' % modPath
                    )
            g = { 'mibBuilder': self }

            self.mibSymbols[modName] = {} # to stop recursion
            
            try:
                execfile(modPath, g)
            except StandardError, why:
                raise error.SmiError(
                    'MIB module %s load error: %s' % (modPath, why)
                )

        self.lastBuildId = self.lastBuildId + 1
        
        return self
                
    def unloadModule(self, *modNames):
        return self

    def importSymbols(self, modName, *symNames):
        r = ()
        for symName in symNames:
            if not self.mibSymbols.has_key(modName):
                self.loadModules(modName)
            if not self.mibSymbols.has_key(modName):
                raise error.SmiError(
                    'No module %s loaded at %s' % (modName, self)
                    )
            if not self.mibSymbols[modName].has_key(symName):
                raise error.SmiError(
                    'No symbol %s::%s at %s' % (modName, symName, self)
                    )
            r = r + (self.mibSymbols[modName][symName],)
        return r

    def exportSymbols(self, modName, **kwargs):
        for symName, symObj in kwargs.items():
            if not self.mibSymbols.has_key(modName):
                self.mibSymbols[modName] = {}
            if self.mibSymbols[modName].has_key(symName):
                raise error.SmiError(
                    'Symbol %s already exported at %s' % (symName, modName)
                    )
            if hasattr(symObj, 'label') and symObj.label:
                symName = symObj.label
            self.mibSymbols[modName][symName] = symObj

# XXX
# get rid of tree MIB structure (index MIB objects by OID name only at MIB
#    instrumentation controller)
# implement by-OID indexing at MIB coltroller
# re-work augmention not to exist at the MibRow level but
#    use name lookups instead
# get rid from subtree registration at MIB modules

