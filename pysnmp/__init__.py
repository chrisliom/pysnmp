"""Various components of SNMP applications"""
from pysnmp import apiver

def getAvailableApiVersions():
    return apiver.listAvailable(__path__[0])

_gCurrentVersion = ''

def setApiVersion(newVer):
    global _gCurrentVersion
    _gCurrentVersion = apiver.importNew(__path__[0], _gCurrentVersion, newVer)

def getApiVersion():
    return _gCurrentVersion
