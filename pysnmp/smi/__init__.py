"""SNMP SMI"""
import os, sys

def getMibTree(*modNames):
    for topDir in map(os.path.normpath, map(
        lambda x: os.path.join(x, 'pysnmp', 'smi', 'backend'), sys.path)):
        try:
            packageNames = os.listdir(topDir)
        except OSError:
            continue
        for packageName in packageNames:
            if packageName[0] == '_':
                continue
            packagePath = os.path.join(topDir, packageName, '__init__.py')
            try:
                execfile(packagePath, globals())
            except:
                continue
            if globals().has_key('MibTree'):
                # XXX when to stop?
                return apply(MibTree, modNames)

#print getMibTree()
