"""MIB variables management"""
from pysnmp.asn1.univ import Integer
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

    # Create operation
    
    def createCheck(self, name, val):
        if name == self.name:
            if self.maxAccess != 'readcreate':
                raise error.NoCreationError(
                    'Varaible creation prohibited at %r' % self
                    )
        else:
            raise error.NoSuchInstanceError(
                'Variable %s does not exist at %r' % (name, self)
                )
        
    def createReserve(self, name, val):
        raise error.NotImplementedError(
            'Creation not implemented at %r' % self
            )

    createCommit = createRelease = createRollback = createReserve

    # Destroy operation
    
    def destroyCheck(self, name, val):
        if name == self.name:
            if self.maxAccess != 'readcreate':
                raise error.NoAccessError(
                    'Varaible destruction prohibited at %r' % self
                    )
        else:
            raise error.NoSuchInstanceError(
                'Variable %s does not exist at %r' % (name, self)
                )
        
    def destroyReserve(self, name, val):
        raise error.NotImplementedError(
            'Destruction not implemented at %r' % self
            )

    destroyCommit = destroyRelease = destroyRollback = destroyReserve

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
                    'No write access to variable %r' % str(name)
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

    # Create operation

    def createCheck(self, name, val):
        if name == self.name:
            if self.maxAccess != 'readcreate':
                raise error.NoCreationError(
                    'Variable creation prohibited at %r' % self
                    )
        else:
            return self._passToSubtree('createCheck', name, val)

    def createReserve(self, name, val):
        self._passToSubtree('createReserve', name, val)        

    def createCommit(self, name, val):
        self._passToSubtree('createCommit', name, val)        

    def createRelease(self, name, val):
        self._passToSubtree('createRelease', name, val)        

    def createRollback(self, name, val):
        self._passToSubtree('createRollback', name, val)        
        
    # Destroy operation
    
    def destroyCheck(self, name, val):
        if name == self.name:
            if self.maxAccess != 'readcreate':
                raise error.NoAccessError(
                    'Varaible destruction prohibited at %r' % self
                    )
        else:
            return self._passToSubtree('destroyCheck', name, val)
        
    def destroyReserve(self, name, val):
        self._passToSubtree('destroyReserve', name, val)
        
    def destroyCommit(self, name, val):
        self._passToSubtree('destroyCommit', name, val)

    def destroyRelease(self, name, val):
        self._passToSubtree('destroyRelease', name, val)
        
    def destroyRollback(self, name, val):
        self._passToSubtree('destroyRollback', name, val)

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
                    'No write access to variable %r' % str(name)
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
        self.__newInstance = {}

    def setColumnInitializer(self, mibVar):
        self.columnInitializer = mibVar
        self.columnInitializer.name = self.name
        return self

    # Column creation
    
    def createCheck(self, createName, name, val):
        # Make sure creation allowed
        if self._vars.has_key(createName):
            return
        try:
            self.columnInitializer.createCheck(createName, None)
        except error.NoSuchInstanceError:
            pass
        
    def createReserve(self, createName, name, val):
        # Create a new column instance but not replace the old one
        if self._vars.has_key(createName):
            return
        if self.__newInstance.has_key(createName):
            raise error.SmiError(
                'Column %r instance %s already being created' %
                (self, createName)
                )
        self.__newInstance[createName] = self.columnInitializer.clone(
            createName
            )
        if createName == name:
            try:
                self.__newInstance[createName].writeCheck(name, val)
            except error.RowCreationWanted:
                pass            
            self.__newInstance[createName].writeReserve(name, val)
        
    def createCommit(self, createName, name, val):
        # Commit new instance value
        if self._vars.has_key(createName):
            return
        if createName == name:
            self.__newInstance[createName].writeCommit(name, val)
        # ...commit new column instance
        self._vars[createName], self.__newInstance[createName] = \
                                self.__newInstance[createName], \
                                self._vars.get(createName)

    def createRelease(self, createName, name, val):
        # Drop previous column instance
        if self._vars.has_key(createName):
            return
        if self.__newInstance.has_key(createName):
            del self.__newInstance[createName]
        
    def createRollback(self, createName, name, val):
        # Set back previous column instance, drop the new one
        if self._vars.has_key(createName):
            return
        self._vars[createName], self.__newInstance[createName] = \
                                self.__newInstance[createName], None
        # Remove new instance on rollback
        if self._vars[createName] is None:
            del self._vars[createName]

    # Column destruction
        
    def destroyCheck(self, destroyName, name, val):
        # Make sure destruction is allowed
        if self._vars.has_key(destroyName):
            self._vars[destroyName].destroyCheck(destroyName, val)
            
    def destroyReserve(self, destroyName, name, val):
        pass

    def destroyCommit(self, destroyName, name, val):
        # Make a copy of column instance and take it off the tree
        if self._vars.has_key(destroyName):
            self.__newInstance[destroyName] = self._vars[destroyName]
            del self._vars[destroyName]
        
    def destroyRelease(self, destroyName, name, val):
        # Drop instance copy
        if self.__newInstance.has_key(destroyName):
            del self.__newInstance[destroyName]
            
    def destroyRollback(self, destroyName, name, val):
        # Set back column instance
        if self.__newInstance.has_key(destroyName):
            self._vars[destroyName] = self.__newInstance[destroyName]
            del self.__newInstance[destroyName]
            
    # Set/modify column

    def writeCheck(self, name, val):
        # Besides common checks, request row creation on no-instance
        try:
            # First try the instance
            AbstractMibSubtree.writeCheck(self, name, val)
        except error.NoSuchInstanceError:
            # ...otherwise indicate that a row should be created
            raise error.RowCreationWanted((name, val))

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
        None, stNotExists
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
    defaultSyntax = Integer(stNotExists)
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
        
class TableRow(AbstractMibSubtree):
    """MIB table row. Manages a set of table columns. Implements row
       creation/destruction.
    """
    def __manageColumns(self, action, statusColumnName, val):
        for name, var in self._vars.items():
            getattr(var, action)(
                name+(statusColumnName[-1],), statusColumnName, val
                )

    def writeCheck(self, name, val):
        # Relay check request to column, expect row operation request.
        if not hasattr(self, '__doingCreation'):
            self.__doingCreation = None
        if not hasattr(self, '__doingDestruction'):
            self.__doingDestruction = None
        try:
            self._passToSubtree('writeCheck', name, val)
        except error.RowCreationWanted, why:
            if self.__doingCreation:
                raise SmiError(
                    'Row %r being created (instance %s)' % (self, name)
                    )
            self.__doingCreation = why.why
        except error.RowDestructionWanted, why:
            if self.__doingDestruction:
                raise SmiError(
                    'Row %r being destroyed (instance %s)' % (self, name)
                    )
            self.__doingDestruction = why.why
        if self.__doingCreation:
            self.__manageColumns('createCheck', self.__doingCreation[0],
                                 self.__doingCreation[1])
        elif self.__doingDestruction:
            self.__manageColumns('destroyCheck', self.__doingDestruction[0],
                                 self.__doingDestruction[1])
    
    def writeReserve(self, name, val):
        # Relay request to column object, run row operation if required
        if self.__doingCreation:
            self.__manageColumns('createReserve', self.__doingCreation[0],
                                 self.__doingCreation[1])
        elif self.__doingDestruction:
            self.__manageColumns('destroyReserve', self.__doingDestruction[0],
                                 self.__doingDestruction[1])
        else:
            self._passToSubtree('writeReserve', name, val)
    
    def writeCommit(self, name, val):
        # Relay request to column object, run row operation if required        
        if self.__doingCreation:
            self.__manageColumns('createCommit', self.__doingCreation[0],
                                 self.__doingCreation[1])
        elif self.__doingDestruction:
            self.__manageColumns('destroyCommit', self.__doingDestruction[0],
                                 self.__doingDestruction[1])
        else:
            self._passToSubtree('writeCommit', name, val)
    
    def writeRelease(self, name, val):
        # Relay request to column object, run row operation if required,
        # cleanup row operation state.
        if self.__doingCreation:
            self.__manageColumns('createRelease', self.__doingCreation[0],
                                 self.__doingCreation[1])
            self.__doingCreation = None
        elif self.__doingDestruction:
            self.__manageColumns('destroyRelease', self.__doingDestruction[0],
                                 self.__doingDestruction[1])
            self.__doingDestruction = None
        else:
            self._passToSubtree('writeRelease', name, val)
    
    def writeRollback(self, name, val):
        # Relay request to column object, run row operation if required,
        # cleanup row operation state.
        if self.__doingCreation:
            self.__manageColumns('createRollback', self.__doingCreation[0],
                                 self.__doingCreation[1])
            self.__doingCreation  = None
        elif self.__doingDestruction:
            self.__manageColumns('destroyRollback', self.__doingDestruction[0],
                                 self.__doingDestruction[1])
            self.__doingDestruction = None
        else:
            self._passToSubtree('writeRollback', name, val)
    
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
    
if __name__ == '__main__':
    from pysnmp.asn1.univ import ObjectIdentifier, Null, Integer

    mv = MibVarManager((1,3),
                       LocalMibSubtree(
        (1,3,1),
        # Pre-initialized table, no creation allowed
        MibTable((1,3,1,1),
                 TableRow((1,3,1,1,1),
                          # read-only var
                          TableColumn((1,3,1,1,1,1),
                                      MibVariable((1,3,1,1,1,1,1),
                                                  Integer(1)
                                                  )
                                      ),
                          # read-write var
                          TableColumn((1,3,1,1,1,2),
                                      MibVariable((1,3,1,1,1,2,1),
                                                  Integer(1)).setAccess('readwrite')
                                      )
                          )
                 ),
        # Table with row creation
        MibTable((1,3,1,2),
                 TableRow((1,3,1,2,1),
                          TableColumn((1,3,1,2,1,1)
                                      ).setColumnInitializer(RowStatus()),
                          # read-write var
                          TableColumn((1,3,1,2,1,2)
                                      ).setColumnInitializer(MibVariable(
        (1,3,1,2,1,2), Integer(1)).setAccess('readcreate')
                                                             )
                          )
                 )
        )
    )

#    print mv.flipFlopFsm(mv.fsmReadVar, ((1,3,1,1,1,2), None))
#    print mv.flipFlopFsm(mv.fsmWriteVar, ((1,3,1,1,1,2,1), Integer(4)))
#    print mv.flipFlopFsm(mv.fsmReadVar, ((1,3,1,1,1,2,1), None))
    
#    print mv.flipFlopFsm(mv.fsmReadVar, ((1,3,1,2,1,1,1), None))
#    print mv.flipFlopFsm(mv.fsmWriteVar, ((1,3,1,2,1,1,1), Integer(4)))
#    print mv.flipFlopFsm(mv.fsmReadVar, ((1,3,1,2,1,1,1), None))
#    print mv.flipFlopFsm(mv.fsmReadVar, ((1,3,1,2,1,2,1), None))
#    print mv.flipFlopFsm(mv.fsmWriteVar, ((1,3,1,2,1,1,1), Integer(6)))
#    print mv.flipFlopFsm(mv.fsmReadVar, ((1,3,1,2,1,2,1), None))
    try:
        print mv.flipFlopFsm(mv.fsmWriteVar,    ((1,3,1,2,1,1,1), Integer(4)))
        print mv.flipFlopFsm(mv.fsmWriteVar,    ((1,3,1,2,1,1,1), Integer(6)))
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

# XXX create access verif at column
