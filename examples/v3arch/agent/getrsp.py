"""Command Responder Application (GET PDU)"""
from pysnmp.proto.rfc3412 import MsgAndPduDispatcher, AbstractApplication
from pysnmp.proto.api import alpha

# PDU version to use
versionId = alpha.protoVersionId1
ver = alpha.protoVersions[versionId]

class AgentApplication(AbstractApplication):
    pduTypes = (
        (alpha.protoVersionId1, \
         alpha.protoVersions[alpha.protoVersionId1].GetRequestPdu.tagSet),
        (alpha.protoVersionId2c, \
         alpha.protoVersions[alpha.protoVersionId2c].GetRequestPdu.tagSet),
        )

    def processPdu(self, msgAndPduDsp, **kwargs):
        # Make response PDU
        reqPdu = kwargs['PDU']
        rspPdu = reqPdu.apiAlphaReply()

        # Produce response var-binds
        varBinds = []
        for varBind in reqPdu.apiAlphaGetVarBindList():
            oid, val = varBind.apiAlphaGetOidVal()
            val = alpha.protoVersions[kwargs['pduVersion']].OctetString(
                'your value is %s' %  val
                )
            varBinds.append((oid, val))
        apply(rspPdu.apiAlphaSetVarBindList, varBinds)

        # Send response
        msgAndPduDsp.returnResponsePdu(
            PDU=rspPdu,
            stateReference=kwargs['stateReference']
            )

msgAndPduDsp = MsgAndPduDispatcher()

# UDP is default transport, initialize client mode
msgAndPduDsp.transportDispatcher.getTransport('udp').openServerMode(
    ('127.0.0.1', 1161)
    )

# Configure target SNMP agent at LCD
( snmpCommunityEntry, )  \
  =  msgAndPduDsp.mibInstrumController.mibBuilder.importSymbols(
    'SNMP-COMMUNITY-MIB', 'snmpCommunityEntry'
    )
msgAndPduDsp.mibInstrumController.writeVars(
    (snmpCommunityEntry.getInstNameByIndex(2, 'myManagerIdx'), 'public'),
    (snmpCommunityEntry.getInstNameByIndex(3, 'myManagerIdx'), 'myManager')
    )

agentApplication = AgentApplication()
msgAndPduDsp.registerContextEngineId(agentApplication)
msgAndPduDsp.transportDispatcher.runDispatcher()
