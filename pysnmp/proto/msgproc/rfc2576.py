# SNMP v1 & v2c message processing models implementation
from pysnmp.proto.msgproc.base import AbstractMessageProcessingModel
from pysnmp.proto.secmod.rfc2576 import SnmpV1SecurityModel, SnmpV2cSecurityModel
from pysnmp.proto import rfc1157, rfc1905, rfc3411, error
import pysnmp.asn1.encoding.ber.error, pysnmp.asn1.error

__all__ = [ 'SnmpV1MessageProcessingModel', 'SnmpV2cMessageProcessingModel' ]

snmpV1MessageProcessingModelId = rfc1157.Version().get()

# Since I have not found a detailed reference to v1MP/v2cMP
# inner workings, the following has been patterned from v3MP. Most
# references here goes to RFC3412.

# XXX?
class V1Pdus(rfc1157.Pdus):
    # This replaces Pdus Message component to stop futher BER stream parse
    def decodeItem(self, octetStream, codecId=None):
        self.wholePdu = octetStream
        return ''

class V2cPdus(rfc1905.Pdus):
    # This replaces Pdus Message component to stop futher BER stream parse
    def decodeItem(self, octetStream, codecId=None):
        self.wholePdu = octetStream
        return ''

class SnmpV1MessageProcessingModel(AbstractMessageProcessingModel):
    defaultMessageProcessingModel = 0
    defaultSecurityModel = 1
    defaultSecurityLevel = 'noAuthNoPriv'
    defaultPduVersion = 0
    defaultSecurityModule = SnmpV1SecurityModel
    
    # Message processing subsystem for SNMP v1
    def __init__(self, mibInstrumController=None):
        AbstractMessageProcessingModel.__init__(self, mibInstrumController)
        self.securityModel = self.defaultSecurityModule(mibInstrumController)

    # rfc3412: 7.1
    def __prepareResponseOrOutgoingMessage(self, **kwargs):
        pdu = kwargs.get('PDU')
        smInParams = {
            'messageProcessingModel': self.defaultMessageProcessingModel,
            'securityModel': self.defaultSecurityModel,
            'securityLevel': self.defaultSecurityLevel,
            'pduVersion': self.defaultPduVersion
            }

        smInParams.update(kwargs)

        snmpEngineID, = self.mibInstrumController.mibBuilder.importSymbols(
            'SNMP-FRAMEWORK-MIB', 'snmpEngineID'
            )
        snmpEngineID = snmpEngineID.syntax.get()

        # rfc3412: 7.1.1.a
        if isinstance(pdu, (rfc3411.ReadClassMixIn,
                            rfc3411.WriteClassMixIn,
                            rfc3411.NotificationClassMixIn)):
            # rfc3412: 7.1.1b
            smInParams['msgID'] = pdu['request_id'].get()

            # Just copy destination address (no re-write available at v1/2c)
            smOutParams = {
                'destTransportDomain': kwargs['transportDomain'],
                'destTransportAddress': kwargs['transportAddress']
                }
        # rfc3412: 7.1.2.a
        elif isinstance(pdu, rfc3411.ResponseClassMixIn):
            # rfc3412: 7.1.2.b
            smInParams.update(
                self._cachePopByStateRef(kwargs['stateReference'])
                )

            # Recover transport details
            smOutParams = {
                'destTransportDomain': smInParams['transportDomain'],
                'destTransportAddress': smInParams['transportAddress']
                }
        else:
            raise error.BadArgumentError(
                'Unsupported PDU class %s at %s' % (pdu, self)
                )

        # rfc3412: 7.1.4
        # Since there's no SNMP engine identification in v1/2c,
        # set destination contextEngineID to ours
        if smInParams.get('contextEngineID') is None:
            smInParams['contextEngineID'] = snmpEngineID

        # rfc3412: 7.1.5
        if smInParams.get('contextName') is None:
            smInParams['contextName'] = ''

        # rfc3412: 7.1.6
        smInParams['scopedPDU'] = (
            smInParams['contextEngineID'],
            smInParams['contextName'],
            pdu
            )

        # rfc3412: 7.1.7
        smInParams['globalData'] = {
            'msgID': pdu['request_id'].get()
            }

        # rfc3412: 7.1.8
        if isinstance(pdu, (rfc3411.ResponseClassMixIn,
                            rfc3411.InternalClassMixIn)):
            smInParams['securityEngineId'] = snmpEngineID

            # rfc3412: 7.1.8.a
            smOutParams.update(apply(
                self.securityModel.generateResponseMsg, (), smInParams
                ))

            # rfc3412: 7.1.8.b
            return smOutParams
        # rfc3412: 7.1.9
        elif isinstance(pdu, (rfc3411.ReadClassMixIn,
                              rfc3411.WriteClassMixIn,
                              rfc3411.NotificationClassMixIn)):
            # rfc3412: 7.1.9.a
            if isinstance(pdu, (rfc3411.UnconfirmedClassMixIn)):
                smInParams['securityEngineID'] = snmpEngineID
            else:
                smInParams['securityEngineID'] = (
                    kwargs.get('transportDomain'), # XXX table lookup -> eID
                    kwargs.get('transportAddress')
                    )
                
            # rfc3412: 7.1.9.b
            smOutParams.update(
                apply(self.securityModel.generateRequestMsg, (), smInParams)
                )
            
            # rfc3412: 7.1.9.c
            if isinstance(pdu, (rfc3411.ConfirmedClassMixIn)):
                # XXX rfc bug? why stateReference should be created?
                self._cachePushByMsgId(
                    smInParams['msgID'],
                    sendPduHandle=smInParams['sendPduHandle'],
                    msgID=smInParams['msgID'],
                    snmpEngineID=snmpEngineID,
                    securityModel=smInParams['securityModel'],
                    securityName=smInParams['securityName'],
                    securityLevel=smInParams['securityLevel'],
                    contextEngineID=smInParams['contextEngineID'],
                    contextName=smInParams['contextName'],
                    transportDomain=kwargs['transportDomain'],
                    transportAddress=kwargs['transportAddress']
                    )
            return smOutParams
            
    prepareOutgoingMessage = __prepareResponseOrOutgoingMessage
    prepareResponseMessage = __prepareResponseOrOutgoingMessage

    # rfc3412: 7.2.1
    
    def prepareDataElements(self, **kwargs):
        # rfc3412: 7.2.2 --> done at MP-level
        
        # rfc3412: 7.2.3
        smInParams = {
            'messageProcessingModel': self.defaultMessageProcessingModel,
            'maxMessageSize': 65000,
            'securityParameters': (kwargs['transportDomain'],
                                   kwargs['transportAddress']),
            'securityModel': self.defaultSecurityModel,
            'securityLevel': self.defaultSecurityLevel,
            'wholeMsg': kwargs['wholeMsg']
            }
        
        # rfc3412: 7.2.4 -- 7.2.5 -> noop

        # rfc3412: 7.2.6
        smOutParams = apply(
            self.securityModel.processIncomingMsg, (), smInParams
            )

        # rfc3412: 7.2.6a, 7.2.6b -> noop

        # rfc3412: 7.2.7
        contextEngineID, contextName, pdu = smOutParams.get('scopedPDU')

        # rfc3412: 7.2.3 (wild hack: use PDU reqID at MsgID)
        smOutParams['msgID'] = pdu['request_id'].get()
        
        # rfc2576: 5.2.1
        mpOutParams = {
            'messageProcessingModel': self.defaultMessageProcessingModel,
            'securityModel': self.defaultSecurityModel,
            'securityName': smOutParams.get('securityName'),
            'securityLevel': self.defaultSecurityLevel,
            'contextEngineID': contextEngineID,
            'contextName': contextName,
            'pduVersion': self.defaultPduVersion,
            'PDU': pdu,
            'pduType': pdu.tagSet,
            'maxSizeResponseScopedPDU':smOutParams['maxSizeResponseScopedPDU'],
            'stateReference': smOutParams['securityStateReference']
            }

        # rfc3412: 7.2.8, 7.2.9 -> noop

        # rfc3412: 7.2.10
        if isinstance(pdu, rfc3411.ResponseClassMixIn):
            # rfc3412: 7.2.10a
            cachedReqParams = self._cachePopByMsgId(smOutParams['msgID'])
            mpOutParams['sendPduHandle'] = cachedReqParams['sendPduHandle']
        else:
            # rfc3412: 7.2.10b
            mpOutParams['sendPduHandle'] = None

        # rfc3412: 7.2.11 -> noop

        # rfc3412: 7.2.12
        if isinstance(pdu, rfc3411.ResponseClassMixIn):
            # rfc3412: 7.2.12a -> noop

            # rfc3412: 7.2.12b
            for key in ('securityModel', 'securityName', # XXX snmpEngineId
                        'securityLevel', 'contextEngineID',
                        'contextName'):
                if mpOutParams[key] != cachedReqParams[key]:
                    raise error.BadArgumentError(
                        'Req/rsp params differ at item %s at %s' % (key, self)
                        )
                        
            # rfc3412: 7.2.12c -> noop

            # rfc3412: 7.2.12d
            return mpOutParams

        # rfc3412: 7.2.13
        if isinstance(pdu, rfc3411.ConfirmedClassMixIn):
            # rfc3412: 7.2.13a
            snmpEngineID, = self.mibInstrumController.mibBuilder.importSymbols(
                'SNMP-FRAMEWORK-MIB', 'snmpEngineID'
                )
            if smOutParams['securityEngineID'] != snmpEngineID.syntax:
                raise error.BadArgumentError(
                    'securityEngineID/snmpEngineID mismatch at %s' % self
                    )

            # rfc3412: 7.2.13b
            mpOutParams['stateReference'] = self._newStateReference()
            self._cachePushByStateRef(
                mpOutParams['stateReference'],
                msgVersion=self.defaultMessageProcessingModel,
                msgID=smOutParams['msgID'],
                securityLevel=mpOutParams['securityLevel'],
                msgMaxSize=smInParams['maxMessageSize'],
                securityModel=mpOutParams['securityModel'],
                maxSizeResponseScopedPDU=mpOutParams['maxSizeResponseScopedPDU'],
                securityStateReference=smOutParams['securityStateReference'],
                transportDomain=kwargs['transportDomain'],
                transportAddress=kwargs['transportAddress']
                )
            
            # rfc3412: 7.2.13c
            return mpOutParams

        # rfc3412: 7.2.14
        if isinstance(pdu, rfc3411.UnconfirmedClassMixIn):
            return mpOutParams
        
snmpV2cMessageProcessingModelId = rfc1905.Version().get()

class SnmpV2cMessageProcessingModel(SnmpV1MessageProcessingModel):
    defaultMessageProcessingModel = 1
    defaultPduVersion = 1
    defaultSecurityModule = SnmpV2cSecurityModel
    
if __name__ == '__main__':
    from pysnmp.smi.objects import module
    from pysnmp.proto import rfc1157

    mib = module.MibModules().loadModules()

    row = mib.getVariable((1,3,6,1,6,3,18,1,1,1))
    mib.writeVars(
        (row.getInstNameByIndex(2, 'mynms'), 'mycomm'),
        (row.getInstNameByIndex(3, 'mynms'), 'mynmsname'),
    )

    mp = SnmpV1MessageProcessingModel(mib)
    
    mpInParams = {
        'PDU': rfc1157.GetRequestPdu(),
        'transportDomain': 'udp',
        'transportAddress': ('127.0.0.1', 161),        
        'securityName': 'mynmsname',
        'sendPduHandle': 33
        }
    
    mpOutParams = apply(mp.prepareOutgoingMessage, (), mpInParams)

    print mpOutParams
    
    mpInParams = {
        'wholeMsg': mpOutParams['wholeMsg'],
        'transportDomain': 'udp',
        'transportAddress': ('127.0.0.1', 1024) 
        }

    mpOutParams = apply(mp.prepareDataElements, (), mpInParams)
    
    print mpOutParams
    
    mpInParams = {
        'securityName': mpOutParams['securityName'],
        'PDU': rfc1157.GetResponsePdu(
        request_id=mpOutParams['PDU']['request_id']
        ),
        'stateReference': mpOutParams['stateReference']
        }
    
    mpOutParams = apply(mp.prepareResponseMessage, (), mpInParams)

    print mpOutParams
    
# XXX
# cache expiration
# why ResponsePdu accepts non ASN1 objects?
