"""Package exception classes"""
from pysnmp import error

class SmiError(error.PySnmpError): pass
class SmiImportError(SmiError): pass
class BadArgumentError(SmiError): pass
class NotImplementedError(SmiError): pass
class MibError(SmiError): pass
class NoSuchInstance(SmiError): pass

