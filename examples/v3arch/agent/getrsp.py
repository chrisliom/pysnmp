"""Command Responder Application (GET PDU)"""
from pysnmp import setApiVersion
setApiVersion('v4')
from pysnmp.proto.rfc3412 import MsgAndPduDispatcher, AbstractApplication
from pysnmp.proto import omni

# PDU version to use
versionId = omni.protoVersionId1
ver = omni.protoVersions[versionId]

class AgentApplication(AbstractApplication):
    pduTypes = (
        (omni.protoVersionId1, \
         omni.protoVersions[omni.protoVersionId1].GetRequestPdu.tagSet),
        (omni.protoVersionId2c, \
         omni.protoVersions[omni.protoVersionId2c].GetRequestPdu.tagSet),
        )

    def processPdu(self, msgAndPduDsp, **kwargs):
        # Make response PDU
        reqPdu = kwargs['PDU']
        rspPdu = reqPdu.omniReply()

        # Produce response var-binds
        varBinds = []
        for varBind in reqPdu.omniGetVarBindList():
            oid, val = varBind.omniGetOidVal()
            val = omni.protoVersions[kwargs['pduVersion']].OctetString(
                'your value is %s' %  val
                )
            varBinds.append((oid, val))
        apply(rspPdu.omniSetVarBindList, varBinds)

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
