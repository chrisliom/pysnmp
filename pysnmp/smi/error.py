"""Package exception classes"""
from pysnmp import error

class SmiError(error.PySnmpError): pass
class SmiImportError(SmiError): pass
class BadArgumentError(SmiError): pass
class NotImplementedError(SmiError): pass
class MibError(SmiError): pass

class MibVariableError(SmiError): pass
class NotInitializedError(MibVariableError): pass
class NoSuchInstanceError(MibVariableError): pass
class InconsistentValueError(MibVariableError): pass
class WrongValueError(MibVariableError): pass
class NoAccessError(MibVariableError): pass
# Row management
class RowCreationWanted(MibVariableError): pass
class RowDestructionWanted(MibVariableError): pass
