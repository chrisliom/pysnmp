"""Implementation of SNMP v.1 (RFC1157)"""

__all__ = [ 'Version', 'Community', 'RequestId', 'ErrorStatus', 'ErrorIndex',\
            'VarBind', 'VarBindList', 'GetRequestPdu', 'GetNextRequestPdu',\
            'GetResponsePdu', 'SetRequestPdu', 'Enterprise', 'AgentAddr',\
            'GenericTrap', 'SpecificTrap', 'TimeStamp', 'TrapPdu', 'Pdus',\
            'Message' ]

from time import time
from pysnmp.asn1 import tags, subtypes
from pysnmp.proto import rfc1155, error
import pysnmp.asn1.error

class Version(rfc1155.Integer):
    subtypeConstraints = ( subtypes.SingleValueConstraint(0), )
    initialValue = 0
    
class Community(rfc1155.OctetString):
    initialValue = 'public'

class InitialRequestIdMixIn:
    # Singular source of req IDs
    globalRequestId = 1000 - long(time() / 100 % 1 * 1000)    
    def initialValue(self):
        try:
            self.set(InitialRequestIdMixIn.globalRequestId)
        except pysnmp.asn1.error.ValueConstraintError:
            self.set(InitialRequestIdMixIn.globalRequestId)
        else:
            InitialRequestIdMixIn.globalRequestId = InitialRequestIdMixIn.globalRequestId + 1
            
class RequestId(InitialRequestIdMixIn, rfc1155.Integer): pass
    
class ErrorStatus(rfc1155.Integer):
    initialValue = 0
    subtypeConstraints = ( subtypes.ValueRangeConstraint(0, 5), )
    pduErrors = [ '(noError) No Error',
                  '(tooBig) Response message would have been too large',
                  '(noSuchName) There is no such variable name in this MIB',
                  '(badValue) The value given has the wrong type or length',
                  '(readOnly) No modifications allowed to this object',
                  '(genError) A general failure occured' ]
    
    def __str__(self):
        """Return verbose error message if known
        """
        return '%s: %d (%s)' % (self.__class__.__name__, self.get(),
                                self.pduErrors[self.get()])

class ErrorIndex(rfc1155.Integer):
    initialValue = 0

class VarBind(rfc1155.Sequence):
    # Bind structure
    protoComponents = { 'name': rfc1155.ObjectName(),
                        'value': rfc1155.ObjectSyntax() }
    protoSequence = ( 'name', 'value' )
        
class VarBindList(rfc1155.SequenceOf):
    protoComponent = VarBind()
    
class RequestPdu(rfc1155.Sequence):
    tagSet = rfc1155.Sequence.tagSet.clone(
        tagClass=tags.tagClassContext
        )
    # PDU structure
    protoComponents = { 'request_id': RequestId(),
                        'error_status': ErrorStatus(),
                        'error_index': ErrorIndex(),
                        'variable_bindings': VarBindList() }
    protoSequence = ( 'request_id', 'error_status', 'error_index',
                      'variable_bindings' )

class GetRequestPdu(RequestPdu):
    tagSet = RequestPdu.tagSet.clone(tagId=0x00)

class GetNextRequestPdu(RequestPdu):
    tagSet = RequestPdu.tagSet.clone(tagId=0x01)

class GetResponsePdu(RequestPdu):
    tagSet = RequestPdu.tagSet.clone(tagId=0x02)

class SetRequestPdu(RequestPdu):
    tagSet = RequestPdu.tagSet.clone(tagId=0x03)

# Trap stuff

class Enterprise(rfc1155.ObjectIdentifier):
    initialValue = (1,3,6,1,1,2,3,4,1)

class AgentAddr(rfc1155.NetworkAddress): pass

class GenericTrap(rfc1155.Integer):
    initialValue = 0
    subtypeConstraints = ( subtypes.ValueRangeConstraint(0, 6), )
    verboseTraps = [ 'coldStart', 'warmStart', 'linkDown', 'linkUp', \
                     'authenticationFailure', 'egpNeighborLoss', \
                     'enterpriseSpecific' ]

    def __str__(self):
        return '%s: %d (%s)' % (self.__class__.__name__, self.get(),
                           self.verboseTraps[self.get()])

class SpecificTrap(rfc1155.Integer):
    initialValue = 0

class TimeStamp(rfc1155.TimeTicks):
    def __init__(self, value=int(time())):
        rfc1155.TimeTicks.__init__(self, value)

class TrapPdu(rfc1155.Sequence):
    tagSet = rfc1155.Sequence.tagSet.clone(
        tagClass=tags.tagClassContext, tagId=0x04
        )
    # PDU structure
    protoComponents = { 'enterprise': Enterprise(),
                        'agent_addr': AgentAddr(),
                        'generic_trap': GenericTrap(),
                        'specific_trap': SpecificTrap(),
                        'time_stamp': TimeStamp(),
                        'variable_bindings': VarBindList() }
    protoSequence = ( 'enterprise', 'agent_addr', 'generic_trap',
                      'specific_trap', 'time_stamp', 'variable_bindings' )

class Pdus(rfc1155.Choice):
    protoComponents = { 'get_request': GetRequestPdu(),
                        'get_next_request': GetNextRequestPdu(),
                        'get_response': GetResponsePdu(),
                        'set_request': SetRequestPdu(),
                        'trap': TrapPdu() }
    protoSequence = ( 'get_request', 'get_next_request', 'get_response',
                      'set_request', 'trap' )
    
class Message(rfc1155.Sequence):
    protoComponents = { 'version': Version(),
                        'community': Community(),
                        'pdu': Pdus() }
    protoSequence = ( 'version', 'community', 'pdu' )


    
