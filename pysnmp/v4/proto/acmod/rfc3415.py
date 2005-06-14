# View-based Access Control Model
from pysnmp.smi.error import NoSuchInstanceError
from pysnmp.proto import error

accessModelID = 3

__powOfTwoSeq = [128, 64, 32, 16, 8, 4, 2, 1]

# 3.2
def isAccessAllowed(
    snmpEngine,
    securityModel,
    securityName,
    securityLevel,
    viewType,
    contextName,
    variableName):
    mibInstrumController = snmpEngine.msgAndPduDsp.mibInstrumController 
    # 3.2.1
    vacmContextEntry, = mibInstrumController.mibBuilder.importSymbols('SNMP-VIEW-BASED-ACM-MIB', 'vacmContextEntry')
    tblIdx = vacmContextEntry.getInstIdFromIndices(contextName)
    try:
        vacmContextName = vacmContextEntry.getNode(
            vacmContextEntry.name + (1,) + tblIdx
            ).syntax
    except NoSuchInstanceError:
        raise error.StatusInformation(errorIndication='noSuchContext')    

    # 3.2.2
    vacmSecurityToGroupEntry, = mibInstrumController.mibBuilder.importSymbols(
        'SNMP-VIEW-BASED-ACM-MIB', 'vacmSecurityToGroupEntry'
        )
    tblIdx = vacmSecurityToGroupEntry.getInstIdFromIndices(
        securityModel, securityName
        )
    try:
        vacmGroupName = vacmSecurityToGroupEntry.getNode(
            vacmSecurityToGroupEntry.name + (3,) + tblIdx
            ).syntax
    except NoSuchInstanceError:
        raise error.StatusInformation(errorIndication='noGroupName')

    # 3.2.3
    vacmAccessEntry, = mibInstrumController.mibBuilder.importSymbols(
        'SNMP-VIEW-BASED-ACM-MIB', 'vacmAccessEntry'
        )
    # XXX partial context name match
    tblIdx = vacmAccessEntry.getInstIdFromIndices(
        vacmGroupName, contextName, securityModel, securityLevel
        )

    # 3.2.4
    if viewType == 'read':
        entryIdx = vacmAccessEntry.name + (5,) + tblIdx
    elif viewType == 'write':
        entryIdx = vacmAccessEntry.name + (6,) + tblIdx
    elif viewType == 'notify':
        entryIdx = vacmAccessEntry.name + (7,) + tblIdx
    else:
        raise error.ProtocolError('Unknown view type %s' % viewType)

    try:
        viewName = vacmAccessEntry.getNode(entryIdx).syntax
    except NoSuchInstanceError:
        raise error.StatusInformation(errorIndication='noAccessEntry')
    if not len(viewName):
        raise error.StatusInformation(errorIndication='noSuchView')

    # XXX split onto object & instance ?
    
    # 3.2.5a
    vacmViewTreeFamilyEntry, = mibInstrumController.mibBuilder.importSymbols('SNMP-VIEW-BASED-ACM-MIB', 'vacmViewTreeFamilyEntry')
    tblIdx = vacmViewTreeFamilyEntry.getInstIdFromIndices(viewName)

    # Walk over entries
    initialTreeName = treeName = vacmViewTreeFamilyEntry.name + (2,) + tblIdx
    maskName = vacmViewTreeFamilyEntry.name + (3,) + tblIdx
    while 1:
        vacmViewTreeFamilySubtree = vacmViewTreeFamilyEntry.getNextNode(
            treeName
            )
        vacmViewTreeFamilyMask = vacmViewTreeFamilyEntry.getNextNode(
            maskName
            )
        treeName = vacmViewTreeFamilySubtree.name
        maskName = vacmViewTreeFamilyMask.name
        if initialTreeName != treeName[:len(initialTreeName)]:
            # 3.2.5b
            raise error.StatusInformation(errorIndication='notInView')            
        l = len(vacmViewTreeFamilySubtree.syntax)
        if l > len(variableName):
            continue
        if vacmViewTreeFamilyMask.syntax:
            mask = []
            for c in str(vacmViewTreeFamilyMask.syntax):
                mask = mask + map(lambda b,c=ord(c): b&c, __powOfTwoSeq)
            m = len(mask)-1
            idx = l-1
            while idx:
                if idx > m or mask[idx] and \
                   vacmViewTreeFamilySubtree.syntax[idx] != variableName[idx]:
                    break
                idx = idx - 1
            if idx: continue # no match
        else: # no mask
            if vacmViewTreeFamilySubtree.syntax != variableName[:l]:
                continue # no match
        # 3.2.5c
        return error.StatusInformation(errorIndication='accessAllowed')

if __name__ == '__main__':
    from pysnmp.entity import engine, config

    snmpEngine = engine.SnmpEngine()

    config.addRoUser(snmpEngine, 'test-user', 1, (1,3,6,1,2,1,2,2,1,1))
    
    isAccessAllowed(
        snmpEngine, 3, 'test-user', 1, 'read', '', (1,3,6,1,2,1,2,2,1,1,22)
        )
    
# XXX
# develop a non-intrum-based management objects access methods
