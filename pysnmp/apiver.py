# API versioning facility. Inspired by similar code of PMW and Twisted.
# App must explicitly set particular API version before importing
# anything else.
import sys, os, string

def listAvailable(prefix):
    def isSubPackage(subDir):
        if subDir and subDir[0] == 'v' and subDir[1] in string.digits \
           and len(subDir) == 2:
            return 1

    subDirs = filter(isSubPackage, os.listdir(prefix))
    subDirs.sort(); subDirs.reverse()
    return subDirs

def importNew(prefix, oldVer, newVer):
    if oldVer == newVer:
        return
    if oldVer:
        raise ImportError(
            'API version %s already imported' % oldVer
            )
    newModName = prefix + '.' + newVer
    __import__(newModName)
    newMod = sys.modules[newModName]
    sys.modules['_real_' + prefix] = sys.modules[prefix]
    sys.modules[prefix] = newMod
    return newVer
        

    
        
            
        
