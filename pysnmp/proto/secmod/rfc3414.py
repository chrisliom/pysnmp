# User-based Security Model for the SNMP v.3 (RFC3414)
from pysnmp.proto import rfc1157, rfc1902, rfc1905, rfc3411, error
from pysnmp.asn1.error import Asn1Error

# 2.4

class UsmSecurityParameters(rfc1902.Sequence):
    """USM security parameters
    """
    # global User-based security parameters
    class MsgAuthoritativeEngineId(rfc1902.OctetString): pass
    class MsgAuthoritativeEngineBoots(rfc1902.Integer):
        valueRangeConstraint = (0, 2147483647)
        initialValue = 0
    class MsgAuthoritativeEngineTime(rfc1902.Integer):
        valueRangeConstraint = (0, 2147483647)
        initialValue = 0
    class MsgUserName(rfc1902.OctetString):
        sizeConstraint = (0, 32)
    # authentication protocol specific parameters
    class MsgAuthenticationParameters(rfc1902.OctetString): pass
    # privacy protocol specific parameters
    class MsgPrivacyParameters(rfc1902.OctetString): pass

    fixedNames = [ 'msgAuthoritativeEngineId', 'msgAuthoritativeEngineBoots',
                   'msgAuthoritativeEngineTime', 'msgUserName',
                   'msgAuthenticationParameters', 'msgPrivacyParameters' ]
    fixedComponents = [ MsgAuthoritativeEngineId, MsgAuthoritativeEngineBoots,
                        MsgAuthoritativeEngineTime, MsgUserName,
                        MsgAuthenticationParameters, MsgPrivacyParameters ]

class UserBasedSecurityModule:
    def __init__(self, mib):
        self.mib = mib
        self.mib.attachNode(pysnmp.smi.rfc3414.SnmpUsmMIB())

        # 2.3
        self.snmpEngines = {}
        
    # These routines manage cache of management apps
    def cacheAdd(self, cachedSecurityData):
        securityStateReference = self.__securityStateRefs.inc(1).get()
        if self.__securityStateRefs.has_key(securityStateReference):
            raise error.BadArgumentError('Attempt to re-use securityStateReference: %s' % str(securityStateReference))
        self.__cachedSecurityData[securityStateReference] = cachedSecurityData
        return securityStateReference

    def cachePop(self, securityStateReference):
        cachedSecurityData = self.__cachedSecurityData.get(securityStateReference)
        if cachedSecurityData is None:
            return
        del self.__cachedSecurityData[securityStateReference]
        return cachedSecurityData
    
    # 2.5.1.1
    def generateRequestMsg(self, **kwargs):
        """A service to generate a Request message
        """
        return apply(self.__generateRequestOrResponseMsg,
                     [ 1 ], kwargs)

    # 2.5.1.2
    def generateResponseMsg(self, **kwargs):
        """A service to generate a Response message
        """
        return apply(self.__generateRequestOrResponseMsg,
                     [ 0 ], kwargs)

    def __generateRequestOrResponseMsg(self, requestMode, **kwargs):
        messageProcessingModel = kwargs.get('messageProcessingModel', None)
        globalData = kwargs.get('globalData', None) # Whole message object
        maxMessageSize = kwargs.get('maxMessageSize', None)
        securityModel = kwargs.get('securityModel', None)
        securityEngineId = kwargs.get('securityEngineId', None)
        securityName = kwargs.get('securityName', None)
        securityLevel = kwargs.get('securityLevel', None)
        scopedPdu = kwargs.get('scopedPdu', None)

        # 3.1.1
        securityStateReference = kwargs.get('securityStateReference', None)

        # 3.1.1a
        if securityStateReference is not None:
            cachedSecurityData = self.cachePop(securityStateReference)
            # XXX
            (usmUserEngineID, usmUserName, usmUserAuthProtocol,
             usmUserPrivProtocol) = cachedSecurityData
            securityEngineId = snmpEngineId
            snmpEngineId = self.mib.searchNode('.1.3.6.1.6.3.10.2.1.1')['type'].getTerminal().get()
        else:
            # 3.1.1b
            idx = 1
            while 1:
                try:
                    usmUserEngineID,
                    usmUserName,
                    usmUserAuthProtocol,
                    usmUserPrivProtocol = lcdGet(self.mib, idx)
                    
                    usmUserName = self.mibObjects.readMextVars(
                        self.mibObjects.columnName(
                        (1,3,6), 
                        getSymbol('SNMPv2-MIB', 'snmpInPkts').syntax.inc(1)

                    
                except pysnmp.asn1.error.BadArgumentError:
                    return ('unknownSecurityName', None)
                if usmUserName == securityName:
                    break
                idx = idx + 1

        # 3.1.2
        if securityLevel == 'AuthPriv':
            if isinstance(usmUserAuthProtocol, \
                          pysnmp.smi.rfc3414.UsmNoAuthProtocol) or \
                          isinstance(usmUserPrivProtocol, \
                                     pysnmp.smi.rfc3414.UsmNoPrivProtocol):
                return ('unsupportedSecurityLevel', None)

        # 3.1.3
        if securityLevel == 'AuthPriv' or securityLevel == 'AuthNoPriv':
            if isinstance(usmUserAuthProtocol, 
                          pysnmp.smi.rfc3414.UsmNoAuthProtocol):
                return ('unsupportedSecurityLevel', None)

        securityParameters = UsmSecurityParameters()
        
        # 3.1.4
        if securityLevel == 'AuthPriv':
            # 3.1.4a
#            privModule = self.privModules.get(usmUserPrivProtocol.__class__,
#                                              None)
#            if privModule is None:
#                return ('unsupportedSecurityLevel', None)

#            (statusInformation, encryptedData, privParameters) = privModule.encryptData(encryptKey=, encryptedData=)
# XXX
            return ('unsupportedSecurityLevel', None)
        else:
            # 3.1.4b
            securityParameters['msgPrivacyParameters'].set('')
            payloadPdu = scopedPdu.encode()
            
        # 3.1.5
        securityParameters['msgAuthoritativeEngineId'].set(securityEngineId)

        # 3.1.6
        if securityLevel == 'AuthPriv' or securityLevel == 'AuthNoPriv':
            # 3.1.6a
            if self.snmpEngines.has_key(securityEngineID):
                (snmpEngineBoots, snmpEngineTime) = \
                                  self.snmpEngines[securityEngineID]
            else:
                raise error.MessageProcessingError('Non-discovered SNMP engine: %s' % str(securityEngineID))
        else:
            # 3.1.6b
            if requestMode is None:
                snmpEngineBoots = self.mib.searchNode('1.3.6.1.6.3.10.2.1.2')['type'].getTerminal().get()
                snmpEngineTime = self.mib.searchNode('1.3.6.1.6.3.10.2.1.3')['type'].getTerminal().get()
            else:
                # 3.1.6c
                snmpEngineBoots = snmpEngineTime = 0

        securityParameters['msgAuthoritativeEngineBoots'].set(snmpEngineBoots)
        securityParameters['msgAuthoritativeEngineTime'].set(snmpEngineTime)

        # 3.1.7
        securityParameters['msgUserName'].set(usmUserName)

        # 3.1.8
        if securityLevel == 'AuthPriv' or securityLevel == 'AuthNoPriv':
            # 3.1.8a
            # XXX
            return ('unsupportedSecurityLevel', None)
        else:
            # 3.1.8b
            securityParameters['msgAuthenticationParameters'].set('')
            globalData['msgData']['plaintext']['data'][None] = scopedPdu
            globalData['msgSecurityParameters'].set(securityParameters.encode())
            wholeMsg = globalData.encode()

        # 3.1.9
        statusInformation = (None, None)
        return (statusInformation, globalData['msgSecurityParameters'].get(),
                wholeMsg)
            
    # 2.5.2
    def processIncomingMsg(self, **kwargs):
        """Process incoming SNMP message
        """
        messageProcessingModel = kwargs.get('messageProcessingModel', None)
        maxMessageSize = kwargs.get('maxMessageSize', None)
        securityModel = kwargs.get('securityModel', None)
        securityLevel = kwargs.get('securityLevel', None)
        wholeMsg = kwargs.get('wholeMsg', None)

        # 3.2.1
        securityParameters = UsmSecurityParameters()
        try:
            securityParameters.decode(kwargs.get('securityParameters', None))
        except Asn1Error:
            # snmpInASNParseErrs
            self.mib.searchNode('.1.3.6.1.1.2.1.11.8')['type'].getTerminal().inc(1)
            return ( 'parseError', None )
        
        # 3.2.2
        securityEngineID = securityParameters['msgAuthoritativeEngineID']
        msgUserName = securityParameters['msgUserName']
        snmpEngineBoots = securityParameters['msgAuthoritativeEngineBoots']
        snmpEngineTime = securityParameters['msgAuthoritativeEngineTime']
        securityStateReference = self.cacheAdd(msgUserName=msgUserName)

        # 3.2.3
        if not securityEngineID or \
           not self.snmpEngines.has_key(securityEngineID) and \
           snmpEngineBoots != 0 and snmpEngineTime != 0:
            # 3.2.3a XXX
            self.snmpEngines[securityEngineID] = (snmpEngineBoots,
                                                  snmpEngineTime)
        else:
            # 3.2.3b
            usmStatsUnknownEngineIDs = self.mib.searchNode('.1.3.6.1.6.3.15.1.1.4')
            usmStatsUnknownEngineIDs['type'].getTerminal().inc(1)
            return ('unknownEngineID', rfc1905.VarBind(name=usmStatsUnknownEngineIDs['value'], value=usmStatsUnknownEngineIDs['type'].getTerminal()))
            
        # 3.2.4
        idx = 1
        while 1:
            try:
                usmUserName = self.mib.searchNode('.1.3.6.1.6.3.15.1.2.2.1.2.%d' % idx)
                usmUserEngineID = self.mib.searchNode('.1.3.6.1.6.3.15.1.2.2.1.1.%d' % idx)
            except pysnmp.asn1.error.BadArgumentError:
                usmStatsUnknownUserNames = self.mib.searchNode('.1.3.6.1.6.3.15.1.1.3')
                usmStatsUnknownUserNames['type'].getTerminal().inc(1)
                return ('unknownSecurityName', rfc1905.VarBind(name=usmStatsUnknownUserNames['value'], value=usmStatsUnknownUserNames['type'].getTerminal()))

            usmUserName = usmUserName['type'].getTerminal().get()
            if usmUserName == msgUserName and \
               usmUserEngineID == securityEngineID:
                usmUserAuthProtocol = self.mib.searchNode('.1.3.6.1.6.3.15.1.2.2.1.5.%d' % idx)['type']
                usmUserPrivProtocol = self.mib.searchNode('.1.3.6.1.6.3.15.1.2.2.1.8.%d' % idx)['type']                        
                break

        # 3.2.5
        if securityLevel == 'AuthPriv' and  \
           isinstance(usmUserAuthProtocol, \
                      pysnmp.smi.rfc3414.UsmNoAuthProtocol) or \
                      isinstance(usmUserPrivProtocol, \
                                 pysnmp.smi.rfc3414.UsmNoPrivProtocol):
                return ('unsupportedSecurityLevel', None)

        
if __name__ == '__main__':
    from time import time
    from pysnmp.asn1 import oidtree
    from pysnmp.smi import rfc1907, rfc3411, rfc3412, rfc3414
    import pysnmp.proto.rfc3412, pysnmp.proto.rfc3411
    import profile

    # Initialize user table

    cell = mib.searchNode('.1.3.6.1.6.3.15.1.2.2.1.2')
    newCell = cell.__class__()
    newCell['value'].set('.1.3.6.1.6.3.15.1.2.2.1.2.1')
    newCell['type'].getTerminal().set('grinch')
    mib.attachNode(newCell)

    cell = mib.searchNode('.1.3.6.1.6.3.15.1.2.2.1.1')
    newCell = cell.__class__()
    newCell['value'].set('.1.3.6.1.6.3.15.1.2.2.1.1.1')
    mib.attachNode(newCell)

    cell = mib.searchNode('.1.3.6.1.6.3.15.1.2.2.1.5')
    newCell = cell.__class__()
    newCell['value'].set('.1.3.6.1.6.3.15.1.2.2.1.5.1')
    mib.attachNode(newCell)

    cell = mib.searchNode('.1.3.6.1.6.3.15.1.2.2.1.8')
    newCell = cell.__class__()
    newCell['value'].set('.1.3.6.1.6.3.15.1.2.2.1.8.1')
    mib.attachNode(newCell)

    r = m.generateRequestMsg(globalData=pysnmp.proto.rfc3412.SnmpV3Message(),
                             maxMessageSize=65535,
                             securityEngineId='0',
                             securityName='grinch',
                             securityLevel='NoAuthNoPriv',
                             scopedPdu=pysnmp.proto.rfc3411.GetRequestPdu())
    print repr(r)

# XXX

from pysnmp.smi.objects import syntax, module, error

mib = module.MibModules().loadModules()

if __name__ == '__main__':
    mib.writeVars(
        (mib.columnarName((1,3,6,1,6,3,18,1,1,1,8), 'router'),
         syntax.Integer(4)),
        (mib.columnarName((1,3,6,1,6,3,18,1,1,1,2),'router'),
         syntax.OctetString('down')),
        (mib.columnarName((1,3,6,1,6,3,18,1,1,1,2),'host'),
         syntax.OctetString('crashed'))
        )

    print repr(mib.getVariable(mib.columnarName((1,3,6,1,6,3,18,1,1,1,2),'host')).syntax)
    
    name, val = (1,3,6), None
    while 1:
        try:
            name, val = mib.readNextVars((name, val))[0]
        except error.NoSuchInstanceError:
            break
        print name, val

