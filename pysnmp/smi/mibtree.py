"""Abstract MIB tree API"""
class AbstractMibTree:
    def __init__(self, *mibModules):
        apply(self.modImport, mibModules)
    
    # Module management API
    
    def modImport(self, *modNames):
        """Import specified (and dependent) modules"""
        pass
    
    def modDrop(self, *modNames):
        """Drop specified modules (with dependence checking)"""
        pass
    
    def getModule(self, modName):
        """Returns a ModuleIdentity object"""
        pass

    def getFirstModule(self):
        """Returns ModuleIdentity object of the first import module"""
        pass

    def getNextModule(self, modName):
        """Returns ModuleIdentity object of the next following module"""
        pass

    # Node management methods
    
    def getOidLabel(self, nodeName):
        """getOidLabel(nodeName) -> (oid, label)"""
        pass

    def getOid(self, nodeName):
        """Resolve MIB object descriptor, name or OID into OID"""
        pass
        
    def getNode(self, nodeName, modName=None):
        """Returns SMI node by OID/label. Instance identifier suffix
           allowed."""
        pass

    def getFirstNode(self, modName=None):
        """Returns the first SMI node by OID/label"""
        pass
    
    def getNextNode(self, nodeName):
        """Returns the next SMI node"""
        pass

    def getParentNode(self, nodeName):
        """Returns the immedate parent SMI node"""
        pass

    def getFirstChildNode(self, nodeName):
        """Returns the first immediate child node"""
        pass

    def getNextChildNode(self, nodeName):
        """Returns the next SMI child node"""
        pass

    # Type management methods

    def getType(self, typeName, modName=None):
        """Returns MibType object (or derivative)"""
        pass
        
    def getFirstType(self, modName):
        """Returns the first type in module as a MibType object
           (or derivative)"""
        pass
        
    def getNextType(self, typeName):
        """Returns next type in module as a MibType object
           (or derivative)"""
        pass
                
    def getParentType(self, typeName):
        """Returns parent type as a MibType object (or derivative)"""
        pass

    def registerType(self, typeNode):
        """Register MibType object (or derivative)"""
        pass

    def unregisterType(self, typeNode):
        """Unregister  MibType object (or derivative)"""
        pass
