"""Command Responder Application (GET PDU)"""
from pysnmp.proto.rfc3412 import MsgAndPduDispatcher, AbstractApplication
from pysnmp.proto import omni
from pysnmp.smi import error

# PDU version to use
versionId = omni.protoVersionId1
ver = omni.protoVersions[versionId]

class AgentApplication(AbstractApplication):
    pduTypes = (
        (omni.protoVersionId1, \
         omni.protoVersions[omni.protoVersionId1].GetNextRequestPdu.tagSet),
        (omni.protoVersionId2c, \
         omni.protoVersions[omni.protoVersionId2c].GetNextRequestPdu.tagSet),
        )

    def processPdu(self, msgAndPduDsp, **kwargs):
        # Make response PDU
        reqPdu = kwargs['PDU']
        rspPdu = reqPdu.omniReply()

        # Pass read-next event to MIB instrumentation
        try:
            varBinds = apply(
                msgAndPduDsp.mibInstrumController.readNextVars,
                map(lambda x: x.omniGetOidVal(),
                    reqPdu.omniGetVarBindList())
                )
        except error.NoSuchInstanceError:
            # Out of MIB
            rspPdu.omniSetEndOfMibIndices(1)
        except error.SmiError:
            rspPdu.omniSetErrorIndex(1)
            rspPdu.omniSetErrorStatus('genError')
        else:
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
