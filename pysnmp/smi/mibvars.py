"""MIB objects interface"""
# mibvar manager -> mibvars
# automatially populated on first reference (special var obj)
# tables are special vars
# table indices not registered to route references through top-level table var

from bisect import bisect
from pysnmp.smi.indices import OidOrderedDict
from pysnmp.smi import error

class MibVariablePattern:
    defaultName = None
    maxAccess = 'readonly'
    def __init__(self, name=None):
        if name is not None:
            self.setName(name)
        elif self.defaultName is not None:
            self.setName(self.defaultName)
        else:
            self.name = None

    def setName(self, name):
        self.name = name
        return self

    def setAccess(self, maxAccess):
        self.maxAccess = maxAccess
        return self

# Defines abstract interface to a scalar MIB variable. Implements get/set
# operation in the way outlined in RFC1157.
class AbstractMibVariable(MibVariablePattern):
    defaultSyntax = None
    def __init__(self, name=None, syntax=None):
        MibVariablePattern.__init__(self, name)
        if syntax is not None:
            self.setSyntax(syntax)
        elif self.defaultSyntax is not None:
            self.setSyntax(self.defaultSyntax.clone())
        else:
            self.syntax = None
            
    def __repr__(self):
        return '%s(%s, %s)' % (
            self.__class__.__name__, self.name, self.syntax
            )

#    def __del__(self):
#        print '%s died' % self
        
    def setSyntax(self, syntax):
        self.syntax = syntax
        return self

    def clone(self, name=None, syntax=None):
        mibVar = self.__class__()
        mibVar.setAccess(self.maxAccess)
        mibVar.setName(self.name); mibVar.setSyntax(self.syntax.clone())
        if name is not None:
            mibVar.setName(name)
        if syntax is not None:
            mibVar.setSyntax(syntax)
        return mibVar
    
    def readCheck(self, name, val):
        if name == self.name:
            if self.maxAccess is not None and \
                   self.maxAccess not in ('readonly', 'readwrite', 'readcreate'):
                raise error.NoAccessError(
                    'No read access to variable %r' % str(name)
                    )
        else:
            raise error.NoSuchInstanceError(
                'Variable %s does not exist at %r' % \
                (name, self.__class__.__name__)
                )
    
    def readGet(self, name, val):
        if name == self.name:
            return self.name, self.syntax

    
    # Two-phase commit implementation

    def writeCheck(self, name, val):
        if name == self.name:
            # make sure variable is writable
            if self.maxAccess not in ('readwrite', 'readcreate'): # XXX create
                raise error.NoAccessError(
                    'No write access to variable %r' % str(name)
                    )
        else:
            raise error.NoSuchInstanceError(
                'Variable %s does not exist at %r' % \
                (name, self.__class__.__name__)
                )

    def writeReserve(self, name, val):
        # Prepare to modify the value
        if not hasattr(self, '_cachedSyntax'):
            self._cachedSyntax = self.syntax.clone()
        if val is not None:
            try:
                self._cachedSyntax.set(val)
            except:
                raise error.WrongValueError(
                    'Value %r is of wrong type at %r' % (val, self)
                    )

    def writeCommit(self, name, val):
        # Commit new value
        self.syntax, self._cachedSyntax = self._cachedSyntax, self.syntax
        
    def writeRelease(self, name, val):
        return self.name, self.syntax
    
    def writeRollback(self, name, val):
        # Revive previous value
        self.syntax, self._cachedSyntax = self._cachedSyntax, self.syntax
        return self.name, self.syntax

class MibVariable(AbstractMibVariable): pass

# Defines abstract API to MIB tree branches. Basically, this acts as proxy
# delegating requests for opearations on a variables (AbstractMibVariable
# API) to inner tree branches (recursively).
# The purpose of this class is to intercept requests to operations on variables
# to control variables creation/removal on the fly (required for MIB tables).
class AbstractMibSubtree(MibVariablePattern):
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
            
    def getSuperTree(self, name):
        superName = tuple(name)
        while len(self.name) < len(superName):
            if self._vars.has_key(superName):
                return superName
            superName = superName[:-1]

    # Abstract API delegation

    def _delegate(self, action, name, val):
        superTreeName = self.getSuperTree(name)
        if superTreeName:
            return getattr(self._vars[superTreeName], action)(name, val)
        else:
            raise error.NoSuchInstanceError(
                'Variable %s does not exist at %r' % (name, self)
                    )

    def readCheck(self, name, val):
        if name == self.name:
            if self.maxAccess is not None and \
                   self.maxAccess not in ('readonly', 'readwrite'):
                raise error.NoAccessError(
                    'No read access to variable %r' % str(name)
                    )
        else:
            return self._delegate('readCheck', name, val)
        
    def readGet(self, name, val):
        return self._delegate('readGet', name, val)

    def __getNextName(self, name):
        nextName = nextWantedFlag = self.getSuperTree(name)
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
        
    def writeCheck(self, name, val):
        if name == self.name:
            # make sure variable is writable
            if self.maxAccess not in ('readwrite', 'readcreate'): # XXX create
                raise error.NoAccessError(
                    'No write access to variable %r' % str(name)
                    )
        else:
            return self._delegate('writeCheck', name, val)                
    def writeReserve(self, name, val):
        return self._delegate('writeReserve', name, val)
    
    def writeCommit(self, name, val):
        return self._delegate('writeCommit', name, val)
    
    def writeRelease(self, name, val):
        return self._delegate('writeRelease', name, val)
    
    def writeRollback(self, name, val):
        return self._delegate('writeRollback', name, val)

class LocalMibSubtree(AbstractMibSubtree): pass

class TableColumn(AbstractMibSubtree):
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
        return self

    # Column creation
    
    def createCheck(self, name, val):
        if self._vars.has_key(name):
            return
        return self.writeCheck(name, None)
        
    def createReserve(self, name, val):
        if self._vars.has_key(name):
            return
        return self.writeReserve(name, None)
        
    def createCommit(self, name, val):
        if self._vars.has_key(name):
            return
        return self.writeCommit(name, None)
        
    def createRelease(self, name, val):
        if self.__newInstance.has_key(name):
            return
        return self.writeRelease(name, None)
        
    def createRollback(self, name, val):
        if not self.__newInstance.has_key(name):
            return
        return self.writeRollback(name, None)

    # Column destruction
        
    def destroyCheck(self, name, val): return

    def destroyReserve(self, name, val): return

    def destroyCommit(self, name, val):
        if self._vars.has_key(name):
            self.__newInstance[name] = self._vars[name]
            del self._vars[name]
        
    def destroyRelease(self, name, val):
        if self.__newInstance.has_key(name):
            del self.__newInstance[name]
            
    def destroyRollback(self, name, val):
        if self.__newInstance.has_key(name):
            self._vars[name] = self.__newInstance[name]
            del self.__newInstance[name]
            
    # Set/modify column

    def writeCheck(self, name, val):
        # Check access and type or see if column allows creation
        try:
            # First try the instance
            return AbstractMibSubtree.writeCheck(self, name, val)
        except error.NoSuchInstanceError:
            # ...then see if it could be created
            superName = name[:-1]
            # Check access and type
            if self.columnInitializer is None:
                raise error.SmiError(
                    'No column syntax for %r at %s' % (name, self)
                    )
            return self.columnInitializer.writeCheck(superName, val)

    def writeReserve(self, name, val):
        # Modify instance or try to create one
        try:
            # Pass to instance
            return AbstractMibSubtree.writeReserve(self, name, val)
        except error.NoSuchInstanceError:
            if self.__newInstance.has_key(name):
                raise error.SmiError(
                    'Column %r instance %s already being created' % (self, name)
                    )
            self.__newInstance[name] = self.columnInitializer.clone(name, val)
            
    def writeCommit(self, name, val):
        # Modify existing instance ot start using new instance
        try:
            # Pass to instance
            return AbstractMibSubtree.writeCommit(self, name, val)
        except error.NoSuchInstanceError:
            # ...commit new value
            self._vars[name], self.__newInstance[name] = \
                              self.__newInstance[name], self._vars.get(name)

    def writeRelease(self, name, val):
        if self.__newInstance.has_key(name):
            del self.__newInstance[name]
            return self._vars[name].syntax
        else:
            # Pass to instance
            return AbstractMibSubtree.writeRelease(self, name, val)

    def writeRollback(self, name, val):
        if self.__newInstance.has_key(name):
            self._vars[name]. self.__newInstance[name] = \
                              self.__newInstance[name], self._vars[name]
            # Remove new instance on rollback
            if self._vars[name] is None:
                del self._vars[name]
            else:
                return self._vars[name].syntax
        else:
            # Pass to instance
            return AbstractMibSubtree.writeRollback(self, name, val)
    
class RowStatus(AbstractMibVariable):
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
    maxAccess = 'readcreate'
    
    def __delegate(self, action, name, val):
        return getattr(AbstractMibVariable, action)(self, name, val)
                                    
    def writeCheck(self, name, val):
        try:
            err, self.__state = self.stateMatrix.get(
                (val.get(), self.syntax.get()), (error.SmiError(
                'Unmatched row state transition %s->%s at %r' %
                (self.syntax, val, self)
                ), None)
                )
            if err is not None:
                raise err()
        except error.RowCreationWanted:
            err = error.RowCreationWanted(name)
        except error.RowDestructionWanted:
            err = error.RowDestructionWanted(name)
        self.__delegate('writeCheck', name, self.__state)
        if err is not None:
            raise err
    def writeReserve(self, name, val):
        return self.__delegate('writeReserve', name, self.__state)
    def writeCommit(self, name, val):
        return self.__delegate('writeCommit', name, self.__state)
    def writeRelease(self, name, val):
        return self.__delegate('writeRelease', name, self.__state)
    def writeRollback(self, name, val):
        return self.__delegate('writeRollback', name, self.__state)
        
    # check:   check if writeable, check data type
    # reserve: create/prepare to destroy row or modify column
    # action: add/destroy/replace row
    # rollback: replace new row with the old one
    # release: delete old row
    
class TableRow(AbstractMibSubtree):
    def __delegate(self, action, name, val):
        return getattr(AbstractMibSubtree, action)(self, name, val)

    def __applyToRow(self, action, statusColumnName, val=None):
        for name, var in self._vars.items():
            if name != statusColumnName[:-1]:
                getattr(var, action)(name+(statusColumnName[-1],), val)
        
    def writeCheck(self, name, val):
        if not hasattr(self, '__doingCreation'):
            self.__doingCreation = None
        if not hasattr(self, '__doingDestruction'):
            self.__doingDestruction = None
        r = None
        try:
            r = self.__delegate('writeCheck', name, val)
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
            self.__applyToRow('createCheck', self.__doingCreation)
        elif self.__doingDestruction:
            self.__applyToRow('destroyCheck', self.__doingDestruction)
        return r
    def writeReserve(self, name, val):
        if self.__doingCreation:
            self.__applyToRow('createReserve', self.__doingCreation)
        elif self.__doingDestruction:
            self.__applyToRow('destroyReserve', self.__doingDestruction)
        return self.__delegate('writeReserve', name, val)
    def writeCommit(self, name, val):
        if self.__doingCreation:
            self.__applyToRow('createCommit', self.__doingCreation)
        elif self.__doingDestruction:
            self.__applyToRow('destroyCommit', self.__doingDestruction)
        return self.__delegate('writeCommit', name, val)
    def writeRelease(self, name, val):
        if self.__doingCreation:
            self.__applyToRow('createRelease', self.__doingCreation)
        elif self.__doingDestruction:
            self.__applyToRow('destroyRelease', self.__doingDestruction)
        self.__doingCreation  = self.__doingDestruction = None
        return self.__delegate('writeRelease', name, val)
    def writeRollback(self, name, val):
        if self.__doingCreation:
            self.__applyToRow('createRollback', self.__doingCreation)
        elif self.__doingDestruction:
            self.__applyToRow('destroyRollback', self.__doingDestruction)
        self.__doingCreation  = self.__doingDestruction = None
        return self.__delegate('writeRollback', name, val)
    
    # check:   check if writeable, check data type
    # reserve: create/prepare to destroy row or modify column
    # action: add/destroy/replace row
    # rollback: replace new row with the old one
    # release: delete old row
    
class MibTable(AbstractMibSubtree): pass
                          
class MibVarManager:
    """Runs FSM, routes var refs to responsible MibVar objects"""
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
        ('writeRelease', 'ok'): 'stop',
        # Rollback on errors at the following states
        ('writeReserve', 'err'): 'writeRollback',
        ('writeCommit', 'err'): 'writeRollback',
        ('writeRollback', 'ok'): 'stop',
        ('*', 'err'): 'stop'
    }

    def __init__(self, mib=None):
        self.mib = mib
        self.__vars = OidOrderedDict()

    def registerVariables(self, *mibVars):
        for mibVar in mibVars:
            oid = tuple(mibVar.name)
            if self.__vars.has_key(oid):
                raise error.BadArgumentError(
                    'Duplicate OID encountered %s' % oid
                    )
            self.__vars[oid] = mibVar

    def unregisterVariables(self, *mibVars):
        for mibVar in mibVars:
            oid = tuple(mibVar.name)
            if self.__vars.has_key(oid):
                del self.__vars[oid]

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
#            print state, status, '->', 
            for name, val in inputNameVals:
                superName = tuple(name)
                while superName:
                    mibVar = self.__vars.get(superName)
                    if mibVar is None:
                        superName = superName[:-1]
                    else:
                        break
                if mibVar is None:
                    raise error.NoSuchInstanceError(
                        'Name %s not supported here' % str(name)
                        )
                f = getattr(mibVar, state, None)
                try:
                    rval = f(name, val)
                except error.MibVariableError, why:
                    myErr = why
                    status = 'err'
                else:
                    status = 'ok'
                    if rval is not None:
                        outputNameVals.append(rval)
#            print status
            
        if myErr:
            raise myErr
        return outputNameVals
    
if __name__ == '__main__':
    from pysnmp.asn1.univ import ObjectIdentifier, Null, Integer

    mv = MibVarManager()
    v=LocalMibSubtree((1,3))
    t=LocalMibSubtree((1,3,1),
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
                                                    ).setColumnInitializer(RowStatus((1,3,1,2,1,1), Integer(0))),
                                        # read-write var
                                        TableColumn((1,3,1,2,1,2)
                                                    ).setColumnInitializer(MibVariable(
        (1,3,1,2,1,2), Integer(1)).setAccess('readwrite')
                                                                )
                                        )
                               )
                      )
    
    mv.registerVariables(t)
#    print mv.flipFlopFsm(mv.fsmReadVar, ((1,3,1,1,1,2), None))
#    print mv.flipFlopFsm(mv.fsmWriteVar, ((1,3,1,1,1,2,1), Integer(4)))
#    print mv.flipFlopFsm(mv.fsmReadVar, ((1,3,1,1,1,2,1), None))
    
#    print mv.flipFlopFsm(mv.fsmReadVar, ((1,3,1,2,1,1,1), None))
#    print mv.flipFlopFsm(mv.fsmWriteVar, ((1,3,1,2,1,1,1), Integer(4)))
#    print mv.flipFlopFsm(mv.fsmReadVar, ((1,3,1,2,1,1,1), None))
#    print mv.flipFlopFsm(mv.fsmReadVar, ((1,3,1,2,1,2,1), None))
#    print mv.flipFlopFsm(mv.fsmWriteVar, ((1,3,1,2,1,1,1), Integer(6)))
#    print mv.flipFlopFsm(mv.fsmReadVar, ((1,3,1,2,1,2,1), None))
    print mv.flipFlopFsm(mv.fsmWriteVar,    ((1,3,1,2,1,1,1), Integer(4)))
    print mv.flipFlopFsm(mv.fsmReadNextVar, ((1,3,1,2,1,1), None))

    name, val = (1, 3, 1), None
    while 1:
        name, val = mv.flipFlopFsm(mv.fsmReadNextVar, (name, val))[0]
        print name, val

# XXX MibManager should rely upon MibSubtree
