"""MIB variables management"""
from string import join, split
from pysnmp.proto import rfc1155
from pysnmp.smi.indices import OidOrderedDict
from pysnmp.smi import error

class MibVariablePattern:
    # Implements primitive features of MIB variable objects
    defaultName = None
    maxAccess = 'readonly'
    def __init__(self, name=None):
        if name is not None:
            self.name = name
        elif self.defaultName is not None:
            self.name = self.defaultName
        else:
            self.name = None

    def setName(self, name):
        self.name = name
        return self

    def setAccess(self, maxAccess):
        self.maxAccess = maxAccess
        return self

class AbstractMibVariable(MibVariablePattern):
    # Defines abstract interface to MIB variables. Implements multi-pass
    # read and write operations as specified by RFC1157.
    defaultSyntax = None
    def __init__(self, name=None, syntax=None):
        MibVariablePattern.__init__(self, name)
        if syntax is not None:
            self.syntax = syntax
        elif self.defaultSyntax is not None:
            self.syntax = self.defaultSyntax.clone()
            self.syntax.set(self.defaultSyntax)      # XXX
        else:
            self.syntax = None
        self.__newValue = None
            
    def __repr__(self):
        return '%s(%s, %s)' % (
            self.__class__.__name__, self.name, self.syntax
            )

    def setSyntax(self, syntax):
        self.syntax = syntax
        return self

    def clone(self, name=None, syntax=None):
        mibVar = self.__class__()
        mibVar.maxAccess = self.maxAccess
        mibVar.name =  self.name
        if self.syntax is not None:
            mibVar.syntax = self.syntax.clone()
            mibVar.syntax.set(self.syntax)
        if name is not None:
            mibVar.name = name
        if syntax is not None:
            mibVar.syntax = syntax
        return mibVar

    # Read operation
    
    def readCheck(self, name, val):
        if name == self.name:
            if self.maxAccess != 'readonly' and \
               self.maxAccess != 'readwrite' and \
               self.maxAccess != 'readcreate':
                raise error.NoAccessError(
                    'No read access to variable %r' % str(name)
                    )
        else:
            raise error.NoSuchInstanceError(
                'Variable %s does not exist at %r' % (name, self)
                )
    
    def readGet(self, name, val):
        # Return current variable (name, value). This is the only API method
        # capable of returning anything!
        if name == self.name:
            return self.name, self.syntax
    
    # Two-phase commit implementation

    def writeCheck(self, name, val):
        # Make sure write's allowed
        if name == self.name:
            # make sure variable is writable
            if self.maxAccess != 'readwrite' and \
               self.maxAccess != 'readcreate':
                raise error.NotWritableError(
                    'No write access to variable %r at %r' % (name, self)
                    )
        else:
            raise error.NoSuchInstanceError(
                'Variable %s does not exist at %r' % (name, self)
                )

    def writeReserve(self, name, val):
        # Initialize new value
        self.__newSyntax = self.syntax.clone()
        try:
            self.__newSyntax.set(val)
        except:
            raise error.WrongValueError(
                'Value %r is of wrong type at %r' % (val, self)
                )

    def writeCommit(self, name, val):
        # Commit new value
        self.syntax, self.__newSyntax = self.__newSyntax, self.syntax
        
    def writeRelease(self, name, val):
        # Drop previous value
        self.__newSyntax = None
    
    def writeRollback(self, name, val):
        # Revive previous value
        self.syntax, self.__newSyntax = self.__newSyntax, None

class MibVariable(AbstractMibVariable):
    """Scalar MIB variable instance"""

class MibSubtreePattern(MibVariablePattern):
    # Manages a tree of AbstractMibVariable's instances.
    defaultVars = None
    maxAccess = "not-accessible"    
    def __init__(self, name=None, *vars):
        MibVariablePattern.__init__(self, name)        
        self._vars = OidOrderedDict()            
        if vars:
            apply(self.registerSubtrees, vars)
        if self.defaultVars:
            apply(self.registerSubtrees,
                  map(lambda x: x.clone(), self.defaultVars)
                  )

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__, self.name
            )

    def registerSubtrees(self, *subTrees):
        for subTree in subTrees:
            if self._vars.has_key(subTree.name):
                raise error.SmiError(
                    'MIB subtree %r already registered %r' % \
                    (subTree.name, self)
                    )
            self._vars[subTree.name] = subTree

    def unregisterSubtrees(self, *subTrees):
        for subTree in subTrees:
            if self._vars.has_key(subTree.name):
                del self._vars[subTree.name]
            
    def getSubtree(self, name):
        subName = tuple(name)
        while len(self.name) < len(subName):
            if self._vars.has_key(subName):
                return subName
            subName = subName[:-1]

    # Mapping interface to subtree
    
    def get(self, key, defVal=None): return self._vars.get(key, defVal)

class AbstractMibSubtree(MibSubtreePattern):
    # Implements AbstractMibVariable API at the tree management class.
    # Basically, this acts as a proxy to scalar tree leaves.
    def _passToSubtree(self, action, name, val):
        subtreeName = self.getSubtree(name)
        if subtreeName:
            return getattr(self._vars[subtreeName], action)(name, val)
        else:
            raise error.NoSuchInstanceError(
                'Variable %s does not exist at %r' % (name, self)
                    )

    # Read operation
    
    def readCheck(self, name, val):
        if name == self.name:
            if self.maxAccess != 'readonly' and \
                   self.maxAccess != 'readwrite' and \
                   self.maxAccess != 'readcreate':                   
                raise error.NoAccessError(
                    'No read access to variable at %r' % self
                    )
        else:
            self._passToSubtree('readCheck', name, val)
        
    def readGet(self, name, val):
        return self._passToSubtree('readGet', name, val)

    # Read next operation is subtree-specific
    
    def __getNextName(self, name):
        nextName = nextWantedFlag = self.getSubtree(name)
        if not nextName:
            if self._vars:
                nextName = self._vars.keys()[0]
            else:
                return
        if isinstance(self._vars[nextName], AbstractMibVariable):
            if nextWantedFlag:
                return self._vars.nextKey(nextName)
            else:
                return nextName
        else:
            r = self._vars[nextName].__getNextName(name)
            if r:
                return r
            else:
                return self._vars.nextKey(nextName)

    def readCheckNext(self, name, val):
        nextName = name
        while 1:
            nextName = self.__getNextName(nextName)
            if nextName:
                try:
                    return self.readCheck(nextName, val)
                except error.NoAccessError:
                    continue
            else:
                raise error.NoSuchInstanceError(
                    'Variable next to %s does not exist at %r' % (name, self)
                    )
    
    def readGetNext(self, name, val):
        nextName = name
        while 1:
            nextName = self.__getNextName(nextName)
            if nextName:
                try:
                    self.readCheck(nextName, val) # XXX
                except error.NoAccessError:
                    continue
                else:
                    return self.readGet(nextName, val)
            else:
                raise error.NoSuchInstanceError(
                    'Variable next to %s does not exist at %r' % (name, self)
                    )

    # Write operation
    
    def writeCheck(self, name, val):
        if name == self.name:
            # make sure variable is writable
            if self.maxAccess != 'readwrite' and \
                   self.maxAccess != 'readcreate':
                raise error.NotWritableError(
                    'No write access to variable %r at %r' % (name, self)
                    )
        else:
            self._passToSubtree('writeCheck', name, val)                

    def writeReserve(self, name, val):
        self._passToSubtree('writeReserve', name, val)
    
    def writeCommit(self, name, val):
        self._passToSubtree('writeCommit', name, val)
    
    def writeRelease(self, name, val):
        self._passToSubtree('writeRelease', name, val)
    
    def writeRollback(self, name, val):
        self._passToSubtree('writeRollback', name, val)

class LocalMibSubtree(AbstractMibSubtree):
    """Local (e.g. existing within the same process) MIB subtree"""

class TableColumn(AbstractMibSubtree):
    """MIB table column. Manages a set of column instance variables"""
    defaultColumnInitializer = None

    def __init__(self, name=None, *vars):
        apply(AbstractMibSubtree.__init__, (self, name) + vars)
        if self.defaultColumnInitializer is not None:
            self.setColumnInitializer(self.defaultColumnInitializer.clone())
        else:
            self.columnInitializer = None
        self.__createdInstances = {}; self.__destroyedInstances = {}
        self.__rowOpWanted = {}

    def setColumnInitializer(self, mibVar):
        self.columnInitializer = mibVar
        self.columnInitializer.name = self.name
        return self

    # Column creation (this should probably be converted into some state
    # machine for clarity). Also, it might be a good idea to inidicate
    # defaulted cols creation in a clearer way than just a val == None.
    
    def createCheck(self, name, val=None):
        # Make sure creation allowed
        if self._vars.has_key(name):
            return
        if val is not None and \
               self.columnInitializer.maxAccess != 'readcreate':
            raise error.NoCreationError(
                'Column instance creation prohibited at %r' % self
                )

    def createReserve(self, name, val=None):
        # Create a new column instance but do not replace the old one
        if self._vars.has_key(name):
            return
        if not self.__createdInstances.has_key(name):
            self.__createdInstances[name] = self.columnInitializer.clone(
                name
                )
        if val is not None:
            try:
                self.__createdInstances[name].writeCheck(name, val)
            except (error.RowCreationWanted, error.RowDestructionWanted):
                pass            
            try:
                self.__createdInstances[name].writeReserve(name, val)
            except (error.RowCreationWanted, error.RowDestructionWanted):
                pass
            
    def createCommit(self, name, val=None):
        # Commit new instance value
        if self._vars.has_key(name):
            if self.__createdInstances.has_key(name):
                if val is not None:
                    self._vars[name].writeCommit(name, val)
            return
        if val is not None:
            self.__createdInstances[name].writeCommit(name, val)
        # ...commit new column instance
        self._vars[name], self.__createdInstances[name] = \
                          self.__createdInstances[name], self._vars.get(name)

    def createRelease(self, name, val=None):
        # Drop previous column instance
        if self.__createdInstances.has_key(name):
            del self.__createdInstances[name]
            self._vars[name].writeRelease(name, val)
        
    def createRollback(self, name, val=None):
        # Set back previous column instance, drop the new one
        if self.__createdInstances.has_key(name):
            self._vars[name] = self.__createdInstances[name]
            del self.__createdInstances[name]            
            # Remove new instance on rollback
            if self._vars[name] is None:
                del self._vars[name]
            else:
                self._vars[name].writeRollback(name, val)
                
    # Column destruction
        
    def destroyCheck(self, name, val=None):
        # Make sure destruction is allowed
        if self._vars.has_key(name):
            if val is not None and self.columnInitializer.maxAccess != 'readcreate':
                raise error.NoAccessError(
                    'Column instance destruction prohibited at %r' % self
                    )
            
    def destroyReserve(self, name, val=None):
        pass

    def destroyCommit(self, name, val=None):
        # Make a copy of column instance and take it off the tree
        if self._vars.has_key(name):
            self.__destroyedInstances[name] = self._vars[name]
            del self._vars[name]
        
    def destroyRelease(self, name, val=None):
        # Drop instance copy
        if self.__destroyedInstances.has_key(name):
            del self.__destroyedInstances[name]
            
    def destroyRollback(self, name, val=None):
        # Set back column instance
        if self.__destroyedInstances.has_key(name):
            self._vars[name] = self.__destroyedInstances[name]
            del self.__destroyedInstances[name]
            
    # Set/modify column

    def writeCheck(self, name, val):
        # Besides common checks, request row creation on no-instance
        try:
            # First try the instance
            AbstractMibSubtree.writeCheck(self, name, val)
        # ...otherwise proceed with creating new column
        except (error.NoSuchInstanceError, error.RowCreationWanted):
            self.__rowOpWanted[name] =  error.RowCreationWanted()
            self.createCheck(name, val)
        except error.RowDestructionWanted:
            self.__rowOpWanted[name] =  error.RowDestructionWanted()
            self.destroyCheck(name, val)
        if self.__rowOpWanted.has_key(name):
            raise self.__rowOpWanted[name]

    def __delegateWrite(self, subAction, name, val):
        if not self.__rowOpWanted.has_key(name):
            getattr(AbstractMibSubtree, 'write'+subAction)(self, name, val)
            return
        if isinstance(self.__rowOpWanted[name], error.RowCreationWanted):
            getattr(self, 'create'+subAction)(name, val)
        if isinstance(self.__rowOpWanted[name], error.RowDestructionWanted):
            getattr(self, 'destroy'+subAction)(name, val)            
        raise self.__rowOpWanted[name]

    def writeReserve(self, name, val):
        self.__delegateWrite('Reserve', name, val)

    def writeCommit(self, name, val):
        self.__delegateWrite('Commit', name, val)

    def writeRelease(self, name, val):
        self.__delegateWrite('Release', name, val)
        if self.__rowOpWanted.has_key(name):
            del self.__rowOpWanted[name]
            
    def writeRollback(self, name, val):
        self.__delegateWrite('Rollback', name, val)
        if self.__rowOpWanted.has_key(name):
            del self.__rowOpWanted[name]
        
class RowStatus(AbstractMibVariable):
    """A special kind of scalar MIB variable responsible for
       MIB table row creation/destruction. See RFC-1903 for details.
    """
    # Known row states
    stNotExists, stActive, stNotInService, stNotReady, \
                 stCreateAndGo, stCreateAndWait, stDestroy = range(7)
    # States transition matrix (see RFC-1903)
    stateMatrix = {
        # (new-state, current-state)  ->  (error, new-state)
        ( stCreateAndGo, stNotExists ): (
        error.RowCreationWanted, stActive
        ),
        ( stCreateAndGo, stNotReady ): (
        error.InconsistentValueError, stNotReady
        ),
        ( stCreateAndGo, stNotInService ): (
        error.InconsistentValueError, stNotInService
        ),
        ( stCreateAndGo, stActive ): (
        error.InconsistentValueError, stActive
        ),
        #
        ( stCreateAndWait, stNotExists ): (
        error.RowCreationWanted, stActive
        ),
        ( stCreateAndWait, stNotReady ): (
        error.InconsistentValueError, stNotReady
        ),
        ( stCreateAndWait, stNotInService ): (
        error.InconsistentValueError, stNotInService
        ),
        ( stCreateAndWait, stActive ): (
        error.InconsistentValueError, stActive
        ),
        #
        ( stActive, stNotExists ): (
        error.InconsistentValueError, stNotExists
        ),
        ( stActive, stNotReady ): (
        error.InconsistentValueError, stNotReady
        ),
        ( stActive, stNotInService ): (
        None, stActive
        ),
        ( stActive, stActive ): (
        None, stActive
        ),
        #
        ( stNotInService, stNotExists ): (
        error.InconsistentValueError, stNotExists
        ),
        ( stNotInService, stNotReady ): (
        error.InconsistentValueError, stNotReady
        ),
        ( stNotInService, stNotInService ): (
        None, stNotInService
        ),
        ( stNotInService, stActive ): (
        None, stActive
        ),
        #
        ( stDestroy, stNotExists ): (
        error.RowDestructionWanted, stNotExists
        ),
        ( stDestroy, stNotReady ): (
        error.RowDestructionWanted, stNotExists
        ),
        ( stDestroy, stNotInService ): (
        error.RowDestructionWanted, stNotExists
        ),
        ( stDestroy, stActive ): (
        error.RowDestructionWanted, stNotExists
        )
        }
    defaultName = ''
    defaultSyntax = rfc1155.Integer(stNotExists)
    maxAccess = 'readcreate'
                                    
    def writeCheck(self, name, val):
        # Run through states transition matrix, executes possible
        # exceptions
        try:
            err, val = self.stateMatrix.get(
                (val.get(), self.syntax.get()), (error.SmiError, None)
                )
            if err is not None:
                raise err(
                    'Failed row state transition at %r -> %s' % (self, val)
                    )
        except error.RowCreationWanted:
            err = error.RowCreationWanted((name, val))
        except error.RowDestructionWanted:
            err = error.RowDestructionWanted((name, val))
        try:
            AbstractMibVariable.writeCheck(self, name, val)
        except error.NoSuchInstanceError:
            pass
        if err is not None:
            raise err

    def writeReserve(self, name, val):
        # Run through states transition matrix, resolve new instance value
        err, val = self.stateMatrix.get(
            (val.get(), self.syntax.get()), (None, None)
            )
        if err is not None:
            error.SmiError(
                'Unmatched row state transition %s->%s at %r' %
                (self.syntax, val, self)
                )            
        AbstractMibVariable.writeReserve(self, name, val)

# Table indices

class IntegerIndex(rfc1155.Integer):
    def setFromName(self, value):
        self.set(value[0])
        return value[1:]
    
    def getAsName(self):
        return (self.get())

class ImpliedOctetStringIndex(rfc1155.OctetString):
    def setFromName(self, value):
        s = reduce(lambda x,y: x+y, map(lambda x: chr(x), value))
        valueLength = 1
        while valueLength < len(s):
            try:
                self.set(s[:valueLength])
                return s[valueLength:]
            except ValueConstraintError:
                valueLength = valueLength + 1
        raise error.SmiError(
            'Instance ID %s does not fit INDEX %r' % (value, self)
            )
    
    def getAsName(self):
        return reduce(lambda x,y: x+y, map(lambda x: ord(x), tuple(self.get())))

class ExpressedOctetStringIndex(rfc1155.OctetString):
    def setFromName(self, value):
        self.set(
            reduce(lambda x,y: x+y, map(lambda x: chr(x), value[1:]))
            )
        return ()

    def getAsName(self):
        return reduce(
            lambda x,y: x+y, map(lambda x: ord(x), self), ord(len(self))
            )

class ImpliedObjectIdentifierIndex(rfc1155.ObjectIdentifier):
    def setFromName(self, value):
        self.set(value)
        return ()

    def getAsName(self):
        return tuple(self)

class ExpressedObjectIdentifierIndex(rfc1155.ObjectIdentifier):
    def setFromName(self, value):
        self.set(value[1:])
        return ()

    def getAsName(self):
        return (len(self),) + tuple(self)

class IpAddressIndex(rfc1155.IpAddress):
    def setFromName(self, value):
        self.set(join(map(str, value), '.'))
        return value[4:]

    def getAsName(self):
        return tuple(map(int, split(self.get(), '.')))    

# Table row (AKA Entry)

class TableRow(AbstractMibSubtree):
    """MIB table row. Manages a set of table columns. Implements row
       creation/destruction.
    """
    defaultIndexNames = None
    __augmentingRows = {}
    
    def __init__(self, name=None, *vars):
        apply(AbstractMibSubtree.__init__, (self, name) + vars)
        if self.defaultIndexNames is not None:
            self.setIndexNames(tuple(self.defaultIndexNames))
        else:
            self.indexNames = None
        self.__augmentingRows[id(self)] = self

    def destroyRow(self):
        del self.__augmentingRows[id(self)]
        
    # Fate sharing mechanics

    def registerAugmentation(self):
        self.__augmentingRows[id(self)] = self

    def unregisterAugmentation(self):
        # This must be called prior to row object deletion
        del self.__augmentingRows[id(self)]

    def announceManagementEvent(self, action, name):
        # Convert OID suffix into index vals
        suffix = name[len(self.name)+1:]
        baseIndices = ()
        for indexName in self.indexNames:
            indexValue = self.get(indexName)
            if indexValue is None:
                # External index
                for rowId, rowValue in self.__augmentingRows.items():
                    for rowIndexName in rowValue.indexNames:
                        if rowIndexName == indexName:
                          indexValue = rowValue.get(indexName)
                          if indexValue is not None:
                              break
                    if indexValue is not None:
                        break
                if indexValue is None:
                    raise error.SmiError(
                        'Unresolved INDEX %r at %r' % (indexName, self)
                        )
            indexValue = indexValue.columnInitializer.clone()
            suffix = indexValue.syntax.setFromName(suffix)
            if self._vars.has_key(indexName):
                baseIndices = baseIndices + (indexValue, )
        if suffix:
            raise error.SmiError(
                'Exsessive instance identifier sub-OIDs left at %r: %r' %
                (self, suffix)
                )
        if not baseIndices:
            return
        myId = id(self)
        for rowId, rowVal in self.__augmentingRows.items():
            if myId != rowId:
                rowVal.receiveManagementEvent(action, baseIndices)
            
    def receiveManagementEvent(self, action, baseIndices):
        # The default inplementation supports one-to-one rows dependency
        newSuffix = ()
        # Resolve indices intersection
        for myIndexName in self.indexNames:
            for baseIndex in baseIndices:
                if baseIndex.name == myIndexName:
                    newSuffix = newSuffix + baseIndex.syntax.getAsName()
        if newSuffix:
            self.__manageColumns(action, newSuffix)

    def setIndexNames(self, *names):
        self.indexNames = tuple(names)
        return self
                             
    def __manageColumns(self, action, nameSuffix):
        for name, var in self._vars.items():
            getattr(var, action)(name + nameSuffix, None)

    def __delegate(self, subAction, name, val):
        # Relay operation request to column, expect row operation request.
        try:
            self._passToSubtree('write'+subAction, name, val)
        except error.RowCreationWanted, why:
            self.__manageColumns('create'+subAction, name[len(self.name)+1:])
            self.announceManagementEvent('create'+subAction, name)
        except error.RowDestructionWanted, why:
            self.__manageColumns('destroy'+subAction, name[len(self.name)+1:])
            self.announceManagementEvent('destroy'+subAction, name)
    
    def writeCheck(self, name, val): self.__delegate('Check', name, val)
    def writeReserve(self, name, val): self.__delegate('Reserve', name, val)
    def writeCommit(self, name, val): self.__delegate('Commit', name, val)
    def writeRelease(self, name, val): self.__delegate('Release', name, val)
    def writeRollback(self, name, val): self.__delegate('Rollback', name, val)
    
class MibTable(AbstractMibSubtree):
    """MIB table"""
                          
class MibVarManager(MibSubtreePattern):
    """Run requested variables through FSM states"""
    fsmReadVar = {
        # ( state, status ) -> newState
        ('start', 'ok'): 'readCheck',
        ('readCheck', 'ok'): 'readGet',
        ('readGet', 'ok'): 'stop',
        ('*', 'err'): 'stop'
    }
    fsmReadNextVar = {
        # ( state, status ) -> newState
        ('start', 'ok'): 'readCheckNext',
        ('readCheckNext', 'ok'): 'readGetNext',
        ('readGetNext', 'ok'): 'stop',
        ('*', 'err'): 'stop'
    }
    fsmWriteVar = {
        # ( state, status ) -> newState
        ('start', 'ok'): 'writeCheck',
        ('writeCheck', 'ok'): 'writeReserve',
        ('writeReserve', 'ok'): 'writeCommit',
        ('writeCommit', 'ok'): 'writeRelease',
        ('writeRelease', 'ok'): 'readCheck',
        # Do read after successful write
        ('readCheck', 'ok'): 'readGet',
        ('readGet', 'ok'): 'stop',
        # Error handling
        ('writeCheck', 'err'): 'writeRelease',        
        ('writeReserve', 'err'): 'writeRelease',
        ('writeCommit', 'err'): 'writeRollback',
        ('writeRollback', 'ok'): 'readCheck',
        # Ignore read errors (removed columns)
        ('readCheck', 'err'): 'stop',
        ('readGet', 'err'): 'stop',
        ('*', 'err'): 'stop'
    }

    def flipFlopFsm(self, fsmTable, *inputNameVals):
        outputNameVals = []
        state, status = 'start', 'ok'
        myErr = None
        while 1:
            fsmState = fsmTable.get((state, status))
            if fsmState is None:
                fsmState = fsmTable.get(('*', status))
                if fsmState is None:
                    raise error.SmiError(
                        'Unresolved FSM state %s, %s' % (state, status)
                        )
            state = fsmState
            if state == 'stop':
                break
            for name, val in inputNameVals:
                subtreeName = self.getSubtree(tuple(name))
                if subtreeName is None:
                    raise error.NoSuchInstanceError(
                        'Variable %s does not exist at %r' % (name, self)
                    )
                f = getattr(self._vars[subtreeName], state, None)
                try:
                    rval = f(name, val)
                except error.MibVariableError, why:
                    if myErr is None:  # Take the first exception
                        myErr = why
                    status = 'err'
                    break
                else:
                    status = 'ok'
                    if rval is not None:
                        outputNameVals.append(rval)
        if myErr:
            raise myErr
        return outputNameVals

    def readVars(self, *vars):
        return apply(self.flipFlopFsm, (self.fsmReadVar, ) + vars)

    def readNextVars(self, *vars):
        return apply(self.flipFlopFsm, (self.fsmReadNextVar, ) + vars)

    def writeVars(self, *vars):
        return apply(self.flipFlopFsm, (self.fsmWriteVar, ) + vars)

if __name__ == '__main__':
    from pysnmp.asn1.univ import ObjectIdentifier, Null, Integer

    mv = MibVarManager((1,3),
                       LocalMibSubtree(
         (1,3,1),
#         # Pre-initialized table, no creation allowed
#         MibTable((1,3,1,1),
#                  TableRow((1,3,1,1,1),
#                           # read-only var
#                           TableColumn((1,3,1,1,1,1),
#                                       MibVariable((1,3,1,1,1,1,1),
#                                                   Integer(1)
#                                                   )
#                                       ),
#                           # read-write var
#                           TableColumn((1,3,1,1,1,2),
#                                       MibVariable((1,3,1,1,1,2,1),
#                                                   Integer(1)).setAccess('readwrite')
#                                       )
#                           )
#                  ),
        # Table with row creation
        MibTable((1,3,1,2),
                 TableRow((1,3,1,2,1),
                          TableColumn((1,3,1,2,1,1)
                                      ).setColumnInitializer(RowStatus()),
                          # read-write var & index
                          TableColumn((1,3,1,2,1,2)
                                      ).setColumnInitializer(MibVariable(
        (1,3,1,2,1,2), IpAddressIndex()).setAccess('readcreate')),
                          ).setIndexNames((1,3,1,2,1,2))
                 ),
         # Augmenting table
         MibTable((1,3,1,3),
                  TableRow((1,3,1,3,1),
                           # read-write var
                           TableColumn((1,3,1,3,1,2)
                                       ).setColumnInitializer(MibVariable(
        (1,3,1,3,1,2), Integer(7871340)).setAccess('readcreate'))
                           ).setIndexNames((1,3,1,2,1,2))
                  )
         ))

    try:
        print mv.flipFlopFsm(mv.fsmWriteVar,
                             ((1,3,1,2,1,1,127,0,0,1), Integer(4)),
                             )
#        print mv.flipFlopFsm(mv.fsmWriteVar,
#                             ((1,3,1,2,1,1,127,0,0,1,1), Integer(6))
#                             )
    except error.SmiError, why:
        print why
#    print mv.flipFlopFsm(mv.fsmReadNextVar, ((1,3,1,2,1), None))

    name, val = (1, 3, 1), None
    while 1:
        try:
            name, val = mv.flipFlopFsm(mv.fsmReadNextVar, (name, val))[0]
        except error.NoSuchInstanceError:
            break
        print name, val

# Column needs fsm for instance management
# inter-table deps:
# * row class keeps refs to row instances
# * on row management op, orig row builds index vals from name suffix and
#   walks other row instances and notifies them about this op
#   (indexName, indexVal), ...
# * notification handler checks that its row has dependency of any of these
#   indices. then builds its column instance identifiers from passed vals and
#   calls its correnspoding management op method.

# XXX
# index methods to all rfc1155 types
# method names -> agentx terms
# layout changes: rfc1155 types and RowStatus into separate modules
