"""
   Message Processing and Dispatching for the SNMP v.3 (RFC3412).

   Written by Ilya Etingof <ilya@glas.net>, 2002-2003.
"""
# Module public names
__all__ = [ 'SnmpV3Message', 'probeVersion' ]

from time import time
from pysnmp.asn1 import oidtree
from pysnmp.proto import rfc1157, rfc1902, rfc1905, rfc3411, rfc3414, error
import pysnmp.smi.rfc1907, pysnmp.smi.rfc3411, pysnmp.smi.rfc3412
import pysnmp.asn1.error

class SnmpV3Message(rfc1902.Sequence):
    """SNMP v.3 message object
    """
    class HeaderData(rfc1902.Sequence):
        """Message administrative parameters
        """
        class Id(rfc1902.Integer):
            """Message ID
            """
            valueRangeConstraint = (0, 2147483647)
            initialValue = 0
            globalRequestId = 0L

            def __init__(self, value=None):
                """Update initial value to autoincrement request-id
                """
                if value is not None:
                    rfc1902.Integer.__init__(self, value)
                    return

                value = self.globalRequestId
                self.globalRequestId = self.globalRequestId + 1
                try:
                    rfc1902.Integer.__init__(self, value)

                except pysnmp.asn1.error.ValueConstraintError:
                    self.globalRequestId = 0L
                    value = self.globalRequestId
                    rfc1902.Integer.__init__(self, value)

        class MaxSize(rfc1902.Integer):
            """Message max size
            """
            valueRangeConstraint = (484, 2147483647)
            initialValue = 65535

        class Flags(rfc1902.OctetString):
            """Message flags
            """
            sizeConstraint = (1, 1)
            singleValueConstraint = [ '\000', '\001', '\003', '\004',
                                      '\005', '\007' ]
            initialValue = singleValueConstraint[0]

            flagNames = { 'NoAuthNoPriv':    0x00,
                          'AuthNoPriv':      0x01,
                          'AuthPriv':        0x03,
                          'ReportableFlag':  0x04 }

            # A partial mapping interface
    
            def __setitem__(self, key, value):
                if key == 'securityLevel':
                    self.set(chr(ord(self.get()) | self.flagNames[value]))
                elif key == 'expectResponse':
                    if value is not None:
                        self.set(chr(ord(self.get()) |
                                     self.flagNames['ReportableFlag']))
                else:
                    raise KeyError, key

            def __getitem__(self, key):
                if key == 'securityLevel':
                    value = ord(self.get()) & ~0x03
                    for key in self.flagNames.keys():
                        if self.flagNames[key] == value:
                            return key
                    else:
                        raise
                elif key == 'expectResponse':
                    if ord(self.get()) & 0x04:
                        return 1
                    else:
                        return 0
                else:
                    raise KeyError, key

            def keys(self): return [ 'securityLevel', 'expectResponse']

        class SecurityModel(rfc1902.Integer):
            """Message security model
            """
            valueRangeConstraint = (0, 2147483647)
            
        fixedNames = [ 'msgId', 'msgMaxSize', 'msgFlags', 'msgSecurityModel' ]
        fixedComponents = [ Id, MaxSize, Flags, SecurityModel ]

    class Version(rfc1902.Integer):
        """Message version
        """
        singleValueConstraint = [ 3 ]
        initialValue = singleValueConstraint[0]

    class SecurityParameters(rfc1902.OctetString):
        """Security model-specific parameters, format
           defined by Security Model
        """
        pass

    class ScopedPduData(rfc1902.Choice):
        """Plaintext or encrypted scoped PDU data
        """
        class ScopedPdu(rfc1902.Sequence):
            """Scoped PDU structure
            """
            class ContextEngineId(rfc1902.OctetString):
                """Uniquely identifies an SNMP entity that may realize an
                   instance of a context with a particular contextName
                """   
                pass

            class ContextName(rfc1902.OctetString):
                """Identifies the particular context associated with the
                   management information contained in the PDU portion of
                   the message
                """
                pass

            class Data(rfc1902.Choice):
                """Opaque PDU data (specific to message processing
                   subsystem). XXX
                """
                # This renders ANY type to a CHOICE of known PDUs XXX
                choiceNames = [ 'get_request', 'get_next_request',
                                'get_bulk_request', 'response', 'set_request',
                                'inform_request', 'snmpV2_trap', 'report' ]
                choiceComponents = [ rfc3411.GetRequestPdu,
                                     rfc3411.GetNextRequestPdu,
                                     rfc3411.GetBulkRequestPdu,
                                     rfc3411.ResponsePdu,
                                     rfc3411.SetRequestPdu,
                                     rfc3411.InformRequestPdu,
                                     rfc3411.SnmpV2TrapPdu,
                                     rfc3411.ReportPdu ]
        
            fixedNames = [ 'contextEngineId', 'contextName', 'data' ]
            fixedComponents = [ ContextEngineId, ContextName, Data ]

        class EncryptedPdu(rfc1902.Sequence):
            """Encrypted scopedPDU value
            """
            pass
        
        choiceNames = [ 'plaintext', 'encryptedPdu' ]
        choiceComponents = [ ScopedPdu, EncryptedPdu ]
        initialComponent = choiceComponents[0]

    fixedNames = [ 'msgVersion', 'msgGlobalData', 'msgSecurityParameters',
                   'msgData' ]
    fixedComponents = [ Version, HeaderData, SecurityParameters,
                        ScopedPduData ]

def probeMessageVersion(wholeMsg):
    class SnmpV3MessageHead(SnmpV3Message):
        fixedNames = [ 'msgVersion' ]
        fixedComponents = [ rfc1902.Integer ]

    msg = SnmpV3MessageHead()
    msg.decode(wholeMsg)
    if msg['msgVersion'] == SnmpV3Message.Version():
        return 1

# Security Models

class SnmpV1SecurityModel:
    """User-based security model
    """
    def __init__(self, mib=None): pass
    def generateRequestMsg(self, msg, **kwargs):
        raise error.NotImplementedError('Security model ' + \
                                        self.__class__.__name__ + \
                                        ' not implemented')

class SnmpV2cSecurityModel:
    """User-based security model
    """
    def __init__(self, mib=None): pass
    def generateRequestMsg(self, msg, **kwargs):
        raise error.NotImplementedError('Security model ' + \
                                        self.__class__.__name__ + \
                                        ' not implemented')

# Message processing subsystems

class v1MP:
    """Message processing subsystem for SNMP version 1
    """
    def __init__(self, mib=None): pass
    def prepareOutgoingMessage(self, **kwargs):
        raise error.NotImplementedError('Message processing model ' + \
                                        self.__class__.__name__ + \
                                        ' not implemented')

    def prepareResponseMessage(self, **kwargs):
        raise error.NotImplementedError('Message processing model ' + \
                                        self.__class__.__name__ + \
                                        ' not implemented')

    def prepareDataElements(self, wholeMsg):
        raise error.NotImplementedError('Message processing model ' + \
                                        self.__class__.__name__ + \
                                        ' not implemented')

class v2cMP(v1MP): pass

class v3MP:
    """Message processing subsystem for SNMP version 3
    """
    def __init__(self, mib=None):
        """
        """
        self.mib = mib

        # Pre-defined security models
        self.securityModels = { 1:  SnmpV1SecurityModel(),
                                2:  SnmpV2cSecurityModel(),
                                3:  rfc3414.UserBasedSecurityModel() }

        # Global source for stateReference and cache repositories
        self.__stateRefCounter = rfc1902.Integer(0L)
        self.__stateRefsByStateRef = {}
        self.__stateRefsByMsgId = {}

    # Outstanding requests cache manipulation routines
    
    def cacheAdd(self, **kwargs):
        stateReference = self.__stateRefCounter.inc(1L).get()
        if self.__stateRefsByStateRef.has_key(stateReference):
            raise error.InternalError('stateReference already exists %s' %
                                      str(stateReference))
        msgId = kwargs.get('msgId', None)
        if msgId is None:
            raise error.BadArgumentError('msgId is missing on cache input %s'\
                                         % str(kwargs))
        self.__stateRefsByStateRef[stateReference] = kwargs
        self.__stateRefsByMsgId[msgId] = kwargs
        return stateReference

    def cachePop(self, **kwargs):
        stateReference = kwargs.get('stateReference', None)
        if stateReference is None:
            msgId = kwargs.get('msgId', None)
            if msgId is None:
                raise error.BadArgumentError('No cache search args given')
            cacheEntry = self.__stateRefsByMsgId.get(msgId, None)
        else:
            cacheEntry = self.__stateRefsByStateRef.get(stateReference, None)
        if cacheEntry is None:
            return
        stateReference = cacheEntry['stateReference']
        msgId = cacheEntry['msgId']
        del self.__stateRefsByMsgId.has_key[msgId]
        del self.__stateRefsByStateRef[stateReference]
        return cacheEntry

#    def cacheExpire(self, timeNow=time()):
#        pass
        
    # 7.1.1.a
    
    def prepareOutgoingMessage(self, **kwargs):
        """Prepare either Read, Write or Notification Class PDU for
           sending
        """
        return apply(self._prepareOutgoingOrResponseMessage, [ None ], kwargs)

    # 7.1.2.a
    
    def prepareResponseMessage(self, **kwargs):
        """Prepare either Response or Internal Class PDU for sending
        """
        return apply(self._prepareOutgoingOrResponseMessage, [ 1 ], kwargs)

    def _prepareOutgoingOrResponseMessage(self, responseFlag, **kwargs):
        """Prepare outgoing or response message for sending
        """
        # Extract input values and initialize defaults
        messageProcessingModel = kwargs.get('messageProcessingModel',
                                            SnmpV3Message.Version().get())
        securityModel = kwargs.get('securityModel', 3)
        securityName = kwargs.get('securityName', 'pysnmp')
        securityLevel = kwargs.get('securityLevel', 'NoAuthNoPriv')
        contextEngineId = kwargs.get('contextEngineId', None)
        contextName = kwargs.get('contextName', None)
        pduVersion = kwargs.get('pduVersion', SnmpV3Message.Version().get())
        pdu = kwargs.get('pdu', None)
        snmpEngineId = self.mib.searchNode('1.3.6.1.6.3.10.2.1.1')['type'].getTerminal().get()
        
        if responseFlag:
            maxSizeResponseScopedPdu = kwargs.get('maxSizeResponseScopedPdu', 65535)
            stateReference = kwargs.get('stateReference', None)
            statusInformation = kwargs.get('statusInformation', (None, None))
        else:
            transportDomain = kwargs.get('transportDomain', '')
            transportAddress = kwargs.get('transportAddress', '')
            expectResponse = kwargs.get('expectResponse', None)
            sendPduHandle = kwargs.get('sendPduHandle', None)
            if sendPduHandle is None:
                raise error.BadArgumentError('Missing sendPduHandle at %s' %\
                                             (self.__class__.__name__))
        
        # 7.1.7{a,c}
        msg = SnmpV3Message()

        if not responseFlag:
            # 7.1.1b
            msg['msgGlobalData']['msgId'].inc(self.mib.searchNode('1.3.6.1.6.3.10.2.1.2')['type'].getTerminal().get() << 16 & 0x7fff0000)
            msgId = msg['msgGlobalData']['msgId']
        else:
            # 7.7.2b
            cacheEntry = self.cachePop(stateReference=stateReference)
            if cacheEntry is None:
                raise error.CacheExpiredError('Request information expired in cache for stateReference %s at %s' % (str(stateReference), self.__class__.__name__))
            msgId = cacheEntry['msgId']
            contextEngineId = cacheEntry['contextEngineId']
            contextName = cacheEntry['contextName']
            securityModel = cacheEntry['securityModel']
            securityName = cacheEntry['securityName']
            securityLevel = cacheEntry['securityLevel']
            securityStateReference = cacheEntry['securityStateReference']
            reportableFlag = cacheEntry['reportableFlag']
            transportDomain = cacheEntry['transportDomain']
            transportAddress = cacheEntry['transportAddress']

            # 7.1.3
            (errorIndication, errorVarBind) = statusInformation
            if errorVarBind is not None:
                # 7.1.3.a
                if reportableFlag == 0:
                    return (statusInformation, None, None, None)

                # 7.1.3.b
                if pdu is not None:
                    requestId = pdu['request_id']
                else:
                    requestId = 0

                    # 7.1.3.c
                    reportPdu = rfc3411.ReportPdu()

                    # 7.1.3.c.1
                    reportPdu['variable_bindings'].append(errorVarBind)

                    # 7.1.3.c.2
                    reportPdu['error_status'] = 0
            
                    # 7.1.3.c.3
                    reportPdu['error_index'] = 0

                    # 7.1.3.c.4
                    reportPdu['request_id'] = requestId

                    # 7.1.3.d
                    (errSecurityLevel, errContextEngineId, errContextName) = \
                                       errorIndication

                    # 7.1.3.d.1
                    if errSecurityLevel is not None:
                        securityLevel = errSecurityLevel
                    else:
                        securityLevel = 'NoAuthNoPriv'

                    # 7.1.3.d.2
                    if errContextEngineId is not None:
                        contextEngineId = errContextEngineId
                    else:
                        contextEngineId = snmpEngineId
                        
                    # 7.1.3.d.3
                    if errContextName is not None:
                        contextName = errContextName
                    else:
                        # set to default context
                        contextName = ''

                    # 7.1.3.e
                    pdu = reportPdu

        # 7.1.4
        if contextEngineId is None:
            contextEngineId = '%s/%s/%d' % (transportDomain,
                                            transportAddress,
                                            id(self))
        # 7.1.5
        if contextName is None:
            contextName = ''

        # 7.1.6
        msg['msgData']['plaintext']['contextEngineId'].set(contextEngineId)
        msg['msgData']['plaintext']['contextName'].set(contextName)
        msg['msgData']['plaintext']['data'][None] = pdu

        # 7.1.7.d
        msg['msgGlobalData']['msgFlags']['securityLevel'] = securityLevel

        # 7.1.7e
        msg['msgGlobalData']['msgSecurityModel'].set(securityModel)

        # 7.1.8
        
        # Make sure we support this securityModel
        securityModule = self.securityModels.get(securityModel, None)
        if securityModule is None:
            raise error.BadArgumentError('Unsupported securityModel: %s'\
                                         % str(securityModel))        
        # set to snmpEngineId        
        securityEngineId = self.mib.searchNode('1.3.6.1.6.3.10.2.1.1')['type'].getTerminal().get()

        # XXX check pdu class
        if responseFlag:
            # 7.1.8.a
            (statusInformation, securityParameters, wholeMsg) = securityModule.generateRequestMsg(msg, messageProcessingModel=messageProcessingModel, securityModel=securityModel, securityEngineId=securityEngineId, securityName=securityName, securityLevel=securityLevel, securityStateReference=securityStateReference)
            (errorIndication, errorVarBind) = statusInformation
            if errorIndication is not None:
                return (statusInformation, None, None, None)
            else:
                # 7.1.8.b
                return (None, transportDomain, transportAddress, wholeMsg)
        # 7.1.9
        else:
            # 7.1.9.a
            if isinstance(pdu, rfc3411.UnconfirmedClass):
                # set to snmpEngineId        
                securityEngineId = self.mib.searchNode('1.3.6.1.6.3.10.2.1.1')['type'].getTerminal().get()
            else:
                snmpEngineId = '%s/%s/%d' % (transportDomain,
                                             transportAddress,
                                             id(self))
                securityEngineId = snmpEngineId

            # 7.1.9.b
            (statusInformation, securityParameters, wholeMsg) = securityModule.generateRequestMsg(msg, messageProcessingModel=messageProcessingModel, securityModel=securityModel, securityEngineId=securityEngineId, securityName=securityName, securityLevel=securityLevel)
            (errorIndication, errorVarBind) = statusInformation
            if errorIndication is not None:
                return (statusInformation, None, None, None)
            else:
                # 7.1.9.c
                if isinstance(pdu, rfc3411.ConfirmedClass):
                    # Cache request information
                    self.cacheAdd(sendPduHandle=sendPduHandle,
                                  msgId=msgId, snmpEngineId=snmpEngineId,
                                  securityModel=securityModel,
                                  securityName=securityName,
                                  securityLevel=securityLevel,
                                  contextEngineId=contextEngineId,
                                  contextName=contextName)

                # 7.1.9.d
                return (None, transportDomain, transportAddress, wholeMsg)

    def prepareDataElements(self, transportDomain, transportAddress, wholeMsg):
        # 7.2.2
        msg = SnmpV3Message()
        try:
            rest = msg.decode(wholeMsg)
        except pysnmp.asn1.error.Asn1Error, why:
            # snmpInASNParseErrs
            self.mib.searchNode('1.3.6.1.1.2.1.11.8')['type'].getTerminal().inc(1)
            return ( 'parseError', None )
            
        # 7.2.3
        msgVersion = msg['msgVersion']
        msgId = msg['msgGlobalData']['msgId']
        msgMaxSize = msg['msgGlobalData']['msgMaxSize']
        msgFlags = msg['msgGlobalData']['msgFlags']
        msgSecurityModel = msg['msgGlobalData']['msgSecurityModel']
        msgSecurityParameters = msg['msgSecurityParameters']
        msgData = msg['msgData']

        # 7.2.4
        securityModule = self.securityModels.get(msgSecurityModel, None)
        if securityModule is None:
            # snmpUnknownSecurityModels
            self.mib.searchNode('1.3.6.1.6.3.11.2.1.1')['type'].getTerminal().inc(1)
            raise error.BadArgumentError('Unsupported securityModel: %s'\
                                         % str(msgSecurityModel))

        # 7.2.5
        securityLevel = msgFlags['securityLevel']
        if securityLevel is None:
            # 7.2.5d (snmpInvalidMsgs)
            self.mib.searchNode('1.3.6.1.6.3.11.2.1.2')['type'].getTerminal().inc(1)
            raise error.BadArgumentError('Strange securityLevel: %s' % \
                                         msgFlags)

        # 7.2.6
        (statusInformation, securityEngineId, securityName, scopedPdu, maxSizeResponseScopedPdu, maxSizeResponseScopedPdu, securityStateReference) = securityModule.processIncomingMsg(messageProcessingModel=SnmpV3Message.Version().get(), maxMessageSize=msgMaxSize, securityParameters=msgSecurityParameters, securityModel=msgSecurityModel, securityLevel=securityLevel, wholeMsg=wholeMsg)

        if statusInformation is not None:
            # 7.2.6a
            (errorIndication, errorVarBind) = statusInformation
            if errorIndication is not None and errorVarBind is not None:
                # 7.2.6a.1
                if scopedPdu is not None:
                    contextEngineId = scopedPdu['contextEngineId']
                    contextName = scopedPdu['contextName']
                    pdu = scopedPdu['data']

                    # 7.2.6a.2
                    stateReference = self.cacheAdd(msgVersion=msgVersion, msgId=msgId, securityLevel=securityLevel, msgFlags=msgFlags, msgMaxSize=msgMaxSize, securityModel=securityModel, maxSizeResponseScopedPdu=maxSizeResponseScopedPeu, securityStateReference=securityStateReference)

                    # 7.2.6a.3
                    # XXX link up to dispatcher?

                    # 7.2.6b
                    raise error.MessageProcessingError('Security module returned failure %s for %s' % (str(errorIndication), str(msg)))

        # 7.2.7
        contextEngineId = scopedPdu['contextEngineId']
        contextName = scopedPdu['contextName']
        pdu = scopedPdu['data']

        # 7.2.8
        pduVersion = pdu.__module__   # Not used

        # 7.2.9
        pduType = pdu.__class__       # Not used

        # 7.2.10
        if isinstance(pdu, rfc3411.ResponseClass) or \
           isinstance(pdu, rfc3411.InternalClass):
            # 7.2.10a
            cacheEntry = self.cachePop(msgId=msgId)
            if cacheEntry is None:
                raise error.MessageProcessingError('No request found in cache for %s' % (str(msg)))

            # 7.2.10b
            sendPduHandle = cacheEntry.get('sendPduHandle', None)

            # 7.2.11
            if isinstance(pdu, rfc3411.InternalClass):
                # 7.2.11a
                statusInformation = (1, pdu['variable_bindings'])

                # 7.2.11b
                cacheEntry = self.cachePop(stateReference=stateReference)
                if cacheEntry is None:
                    raise error.MessageProcessingError('No request found in cache for %s' % (str(msg)))
                if cacheEntry['securityModel'] != securityModel or \
                   cacheEntry['securityLevel'] != securityLevel:
                    raise error.MessageProcessingError('securityModel and/or securityLevel mismatch cached request: %s vs %s' % (str(msg), str(cacheEntry)))

                # 7.2.11c
                securityStateReference = None

                # 7.2.11d
                stateReference = None
                
                # 7.2.11e
                return (messageProcessingModel, securityModel, securityName, securityLevel, contextEngineId, contextName, pduVersion, pdu, pduType, sendPduHandle, maxSizeResponseScopedPdu, statusInformation, stateReference)

            # 7.2.12
            if isinstance(pdu, rfc3411.ResponseClass):
                # 7.2.12a
                cacheEntry = self.cachePop(stateReference=stateReference)
                if cacheEntry is None:
                    raise error.MessageProcessingError('No request found in cache for %s' % (str(msg)))
                snmpEngineId = cacheEntry['']

                # 7.2.12b
                if snmpEngineId != cacheEntry['snmpEngineId'] or \
                   securityModel != cacheEntry['securityModel'] or \
                   securityName != cacheEntry['securityName'] or \
                   securityLevel != cacheEntry['securityLevel'] or \
                   contextEngineId != cacheEntry['contextEngineId'] or \
                   contextName != cacheEntry['contextName']:
                    raise error.MessageProcessingError('Cached req mismatches response: %s vs %s' % (str(msg), str(cacheEntry)))
                    
                # 7.2.12c
                stateReference = None

                # 7.2.12d
                return (messageProcessingModel, securityModel, securityName, securityLevel, contextEngineId, contextName, pduVersion, pdu, pduType, sendPduHandle, maxSizeResponseScopedPdu, statusInformation, stateReference)

        # 7.2.13
        if isinstance(pdu, rfc3411.ConfirmedClass):
            # 7.2.13a
            if securityEngineId != snmpEngineId:
                self.cachePop(msgId=msgId)
                self.cachePop(stateReference=stateReference)
                raise error.MessageProcessingError('securityEngineId != snmpEngineId %s != %s: %s' % (str(securityEngineId), str(snmpEngineId), str(msg)))
                
            # 7.2.13b
            stateReference = self.cacheAdd(msgVersion=msgVersion, msgId=msgId, securityLevel=securityLevel, msgFlags=msgFlags, msgMaxSize=msgMaxSize, securityModel=securityModel, maxSizeResponseScopedPdu=maxSizeResponseScopedPdu, securityStateReference=securityStateReference)

            # 7.2.13c
            return (messageProcessingModel, securityModel, securityName, securityLevel, contextEngineId, contextName, pduVersion, pdu, pduType, sendPduHandle, maxSizeResponseScopedPdu, statusInformation, stateReference)
            
        # 7.2.14
        if isinstance(pdu, rfc3411.UnconfirmedClass):
            return (messageProcessingModel, securityModel, securityName, securityLevel, contextEngineId, contextName, pduVersion, pdu, pduType, sendPduHandle, maxSizeResponseScopedPdu, statusInformation, stateReference)

class Dispatcher:
    """SNMP engine PDU & message dispatcher. Exchanges SNMP PDU's with
       applications and serialized messages with transport level.
    """
    def __init__(self, mib=None):
        """
        """
        if mib is None:
            # Initialize SMI tree
            self.mib = oidtree.Root()

            # ...MIBII
            self.mib.attachNode(pysnmp.smi.rfc1907.Snmp())
            # ...SNMP management
            self.mib.attachNode(pysnmp.smi.rfc3411.SnmpFrameworkMib())
            # ...statistics for SNMP Messages        
            self.mib.attachNode(pysnmp.smi.rfc3412.SnmpMpdMib())
        else:
            self.mib = mib
            
        # Versions to subsystems mapping
        self.messageProcessingSubsystems = { rfc1157.Version().get()
                                             : v1MP(self.mib),
                                             rfc1905.Version().get()
                                             : v2cMP(self.mib), \
                                             SnmpV3Message.Version().get()
                                             : v3MP(self.mib) }

        # Versions to octet-stream probers mapping
        self.messageProcessingModels = { rfc1157.Version().get()
                                         : rfc1157.probeMessageVersion,
                                         rfc1905.Version().get()
                                         : rfc1905.probeMessageVersion,
                                         SnmpV3Message.Version().get()
                                         : probeMessageVersion }

        # Registered context engine IDs
        self.__contextEngineIdSet = {}

        # Source of sendPduHandle and cache of requesting apps
        self.__sendPduHandle = rfc1902.Counter32(0)
        self.__sendPduHandles = {}

    # These routines manage cache of management apps
    def cacheAdd(self, expectResponse):
        sendPduHandle = self.__sendPduHandle.inc(1).get()
        if expectResponse is None:
            return sendPduHandle
        if not has_attr(expectResponse, 'processResponsePdu'):
            raise error.BadArgumentError('Bad callback object: %s' % (str(expectResponse)))
        if self.__sendPduHandles.has_key(sendPduHandle):
            raise error.BadArgumentError('Attempt to re-use sendPduHandle: %s' % str(sendPduHandle))
        self.__sendPduHandles[sendPduHandle] = expectResponse
        return sendPduHandle

    def cachePop(sendPduHandle):
        expectResponse = self.__sendPduHandles.get(sendPduHandle)
        if expectResponse is None:
            return
        del self.__sendPduHandles[sendPduHandle]
        return expectResponse
            
    # Application registration with dispatcher

    # 4.3.1
    def registerContextEngineId(self, contextEngineId, pduType, app):
        """Register contextEngineId/pduType pair with dispatcher
        """
        # 4.3.2
        if contextEngineId is None or pduType is None:
            raise error.BadArgumentError('Bad contextEngineId/pduType values')

        if not hasattr(app, 'processResponsePdu'):
            raise error.BadArgumentError('Missing processResponsePdu() in application object')
        processResponsePdu = getattr(app, 'processResponsePdu')
        if not callable(processResponsePdu):
            raise error.BadArgumentError('Bad processResponsePdu() in app')

        # 4.3.3
        if self.__contextEngineIdSet.has_key((contextEngineId, pduType)):
            raise error.BadArgumentError('Duplicate contextEngineId/pduType pair: ' + str((contextEngineId, pduType)))

        # 4.3.4
        self.__contextEngineIdSet[(contextEngineId, pduType)] = app

    # 4.4.1
    def unregisterContextEngineId(self, contextEngineId, pduType):
        """Unregister contextEngineId/pduType pair with dispatcher
        """
        # 4.4.2
        if contextEngineId is None or pduType is None:
            raise error.BadArgumentError('Bad contextEngineId/pduType values')

        del self.__contextEngineIdSet.has_key[(contextEngineId, pduType)]

    def getRegisteredApp(self, contextEngineId, pduType):
        return self.__contextEngineIdSet.get((contextEngineId, pduType), None)
        
    # 4.1.1
    
    def sendPdu(self, **kwargs):
        """PDU dispatcher -- prepare and serialize a request or notification
        """
        # Extract input values and initialize defaults
        messageProcessingModel = kwargs.get('messageProcessingModel',
                                            SnmpV3Message.Version().get())
        
        # 4.1.1.2
        if self.messageProcessingSubsystems.has_key(messageProcessingModel):
            mpHdl = self.messageProcessingSubsystems[messageProcessingModel]
        else:
            raise error.BadArgumentError('Unknown messageProcessingModel: %s'\
                                         % str(messageProcessingModel))

        # 4.1.1.3
        sendPduHandle = self.cacheAdd(kwargs.get('expectResponse', None))
        kwargs['sendPduHandle'] = sendPduHandle

        # 4.1.1.4
        (statusInformation, transportDomain, \
         transportAddress, wholeMsg) = apply(mpHdl.prepareOutgoingMessage,
                                             [], kwargs)
        
        # 4.1.1.5
        if statusInformation is not None:
            (errorIndication, errorVarBind) = statusInformation
            if errorIndication is not None:
                return statusInformation['errorIndication']

        # 4.1.1.6
        # N/A at this level
        
        return (statusInformation, sendPduHandle, wholeMsg)

    # 4.1.2.1
    def returnResponsePdu(self, **kwargs):
        """PDU dispatcher -- prepare and serialize a response
        """
        # Extract input values and initialize defaults
        messageProcessingModel = kwargs.get('messageProcessingModel',
                                            SnmpV3Message.Version().get())
        securityModel = kwargs.get('securityModel', 3)
        securityName = kwargs.get('securityName', 'pysnmp')
        securityLevel = kwargs.get('securityLevel', 'NoAuthNoPriv')
        contextEngineId = kwargs.get('contextEngineId', None)
        contextName = kwargs.get('contextName', None)
        pduVersion = kwargs.get('pduVersion', SnmpV3Message.Version().get())
        pdu = kwargs.get('pdu', None)
        maxSizeResponseScopedPdu = kwargs.get('maxSizeResponseScopedPdu',
                                              65535)
        stateReference = kwargs.get('stateReference', None)
        statusInformation = kwargs.get('statusInformation', (None, None))

        mpHdl = self.messageProcessingSubsystems.get(messageProcessingModel, None)
        if mpHdl is None:
            raise error.BadArgumentError('Unknown messageProcessingModel: %s'\
                                         % str(messageProcessingModel))

        # 4.1.2.2
        (statusInformation, transportDomain, transportAddress, wholeMsg) = mpHdl.prepareResponseMessage(messageProcessingModel=messageProcessingModel, securityModel=securityModel, securityName=securityName, securityLevel=securityLevel, contextEngineId=contextEngineId, contextName=contextName, pduVersion=pduVersion, pdu=pdu, maxSizeResponseScopedPdu=maxSizeResponseScopedPdu, stateReference=stateReference, statusInformation=statusInformation)
        
        # 4.1.2.3
        if statusInformation is not None:
            (errorIndication, errorVarBind) = statusInformation
            if errorIndication is not None:
                return errorIndication
        
        # 4.1.2.4
        # N/A at this level
        
        return (result, wholeMsg)

    # 4.2.1    
    def receiveMessage(self, transportDomain, transportAddress, wholeMsg):
        """Message dispatcher -- de-serialize message into PDU
        """
        # 4.2.1.1
        
        # snmpInPkts
        self.mib.searchNode('1.3.6.1.1.2.1.11.1')['type'].getTerminal().inc(1)

        # 4.2.1.2
        for (messageProcessingModel, proberFun) in \
            self.messageProcessingModels.items():
            try:
                if proberFun(wholeMsg):
                    break
            except error.Asn1Error:
                self.mib.searchNode('1.3.6.1.1.2.1.11.6')['type'].getTerminal().inc(1)
                return ( 'parseError', None )
        else:
            # snmpInBadVersions
            self.mib.searchNode('1.3.6.1.1.2.1.11.3')['type'].getTerminal().inc(1)
            return ( 'parseError', None )

        # 4.2.1.3 -- no-op

        # 4.2.1.4
        mpHdl = self.messageProcessingSubsystems[messageProcessingModel]
        (messageProcessingModel, securityModel, securityName, securityLevel, contextEngineId, contextName, pduVersion, pdu, pduType, sendPduHandle, maxSizeResponseScopedPdu, statusInformation, stateReference) = mpHdl.prepareDataElements(transportDomain, transportAddress, wholeMsg)

        # 4.2.1.5
        if statusInformation is not None:
            (errorIndication, errorVarBind) = statusInformation
            if errorIndication is not None:
                return

        # 4.2.1.6 no-op

        # 4.2.2
        if sendPduHandle is None:
            # 4.2.2.1 (request or notification)

            # 4.2.2.1.1
            app = self.getRegisteredApp(contextEngineId, pduType)
            
            # 4.2.2.1.2
            if app is None:
                # 4.2.2.1.2.a
                self.mib.searchNode('1.3.6.1.6.3.11.2.1.3')['type'].getTerminal().inc(1)
                # 4.2.2.1.2.b
                statusInformation = (1, rfc1905.VarBind(name=self.mib.searchNode('1.3.6.1.6.3.11.2.1.3')['type'].getTerminal()['value']))
                
                (statusInformation, transportDomain, transportAddress, wholeMsg) = mpHdl.prepareResponseMessage(messageProcessingModel=messageProcessingModel, securityModel=securityModel, securityName=securityName, securityLevel=securityLevel, contextEngineId=contextEngineId, contextName=contextName, pduVersion=pduVersion, pdu=pdu, maxSizeResponseScopedPdu=maxSizeResponseScopedPdu, stateReference=stateReference, statusInformation=statusInformation)

                # 4.2.2.1.2.c
                if statusInformation is not None:
                    # XXX send to originator
                    (errorIndication, errorVarBind) = statusInformation

                # 4.2.2.1.2.d
                return
            else:
                # 4.2.2.1.3
                app.processPdu(messageProcessingModel=messageProcessingModel, securityModel=securityModel, securityName=securityName, securityLevel=securityLevel, contextEngineId=contextEngineId, contextName=contextName, pduVersion=pduVersion, pdu=pdu, maxSizeResponseScopedPdu=maxSizeResponseScopedPdu, stateReference=stateReference)
                return
        else:
            # 4.2.2.2 (response)
            
            # 4.2.2.2.1
            app = self.cachePop(sendPduHandle)

            # 4.2.2.2.2
            if app is None:
                self.mib.searchNode('1.3.6.1.6.3.11.2.1.3')['type'].getTerminal().inc(1)
                return
                
            # 4.2.2.2.3
            # no-op ? XXX

            # 4.2.2.2.4
            app.processResponsePdu(messageProcessingModel=messageProcessingModel, securityModel=securityModel, securityName=securityName, securityLevel=securityLevel, contextEngineId=contextEngineId, contextName=contextName, pduVersion=pduVersion, pdu=pdu, statusInformation=statusInformation, sendPduHandle=sendPduHandle)

if __name__ == '__main__':

    class Application:
        def processResponsePdu(self, **kwargs):
            print repr(kwargs)
            
    mgrDisp = Dispatcher()
    agentDisp = Dispatcher()
    agentDisp.registerContextEngineId('myCtxEngId', rfc1905.GetRequestPdu,
                                      Application())

    # Send msg
    (statusInformation, sendPduHandle, wholeMsg) = mgrDisp.sendPdu(pdu=rfc3411.GetRequestPdu())
    print repr((statusInformation, sendPduHandle, wholeMsg))

    # Recv msg XXX
    agentDisp.receiveMessage(None, None, wholeMsg)

    # Send response
    (result, wholeMsg) = agentDisp.returnResponsePdu(pdu=rfc3411.ResponsePdu(),  sendPduHandle=sendPduHandle)
    print repr((result, wholeMsg))

    # Receive response XXX
    mgrDisp.receiveMessage(None, None, wholeMsg)
