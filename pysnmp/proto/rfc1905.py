"""Implementation of SNMP v.2c (RFC1905)"""

__all__ = [ 'Version', 'Community', 'RequestId', 'NoSuchObject', \
            'NoSuchInstance', 'EndOfMibView', 'BindValue', 'VarBind', \
            'VarBindList', 'Pdu', 'NonRepeaters', 'MaxRepetitions', \
            'GetRequestPdu', 'GetNextRequestPdu', 'ResponsePdu', \
            'SetRequestPdu', 'GetBulkRequestPdu', 'InformRequestPdu', \
            'SnmpV2TrapPdu', 'ReportPdu', 'Pdus', 'Message' ]

from time import time
from pysnmp.asn1 import tags, subtypes
from pysnmp.proto import rfc1902
from pysnmp.proto.rfc1157 import InitialRequestIdMixIn
import pysnmp.asn1.error

# Value reference -- max bindings in VarBindList
max_bindings = rfc1902.Integer(2147483647)

class Version(rfc1902.Integer):
    subtypeConstraints = ( subtypes.SingleValueConstraint(1), )
    initialValue = 1
    
class Community(rfc1902.OctetString):
    initialValue = 'public'    

class RequestId(InitialRequestIdMixIn, rfc1902.Integer): pass

class ErrorStatus(rfc1902.Integer):
    initialValue = 0
    subtypeConstraints = ( subtypes.ValueRangeConstraint(0, 18), )
    pduErrors = [ '(noError) No Error',
                  '(tooBig) Response message would have been too large',
                  '(noSuchName) There is no such variable name in this MIB',
                  '(badValue) The value given has the wrong type or length',
                  '(readOnly) No modifications allowed to this object',
                  '(genError) A general failure occured',
                  '(noAccess) Access denied',
                  '(wrongType) Wrong BER type',
                  '(wrongLength) Wrong BER length',
                  '(wrongEncoding) Wrong BER encoding',
                  '(wrongValue) Wrong value',
                  '(noCreation) Object creation prohibited',
                  '(inconsistentValue) Inconsistent value',
                  '(resourceUnavailable) Resource unavailable',
                  '(commitFailed) Commit failed',
                  '(undoFailed) Undo failed',
                  '(authorizationError) Authorization error',
                  '(notWritable) Object is not writable',
                  '(inconsistentName) Inconsistent object name' ]

    def __str__(self):
        return '%s: %d (%s)' % (self.__class__.__name__, self.get(),
                                self.pduErrors[self.get()])
    
class ErrorIndex(rfc1902.Integer):
    subtypeConstraints = ( subtypes.ValueRangeConstraint(0, max_bindings.get()), )

class NoSuchObject(rfc1902.Null):
    tagSet = rfc1902.Null.tagSet.clone(
        tagClass=tags.tagClassContext, tagId=0x00
        )

class NoSuchInstance(rfc1902.Null):
    tagSet = rfc1902.Null.tagSet.clone(
        tagClass=tags.tagClassContext, tagId=0x01
        )

class EndOfMibView(rfc1902.Null):
    tagSet = rfc1902.Null.tagSet.clone(
        tagClass=tags.tagClassContext, tagId=0x02
        )

class BindValue(rfc1902.Choice):
    protoComponents = { 'value': rfc1902.ObjectSyntax(),
                        'unspecified': rfc1902.Null(),
                        'noSuchObject': NoSuchObject(),
                        'noSuchInstance': NoSuchInstance(),
                        'endOfMibView': EndOfMibView() }
    initialComponentKey = 'unspecified'
    
class VarBind(rfc1902.Sequence):
    # Bind structure
    protoComponents = { 'name': rfc1902.ObjectName(),
                        'value': BindValue() }
    protoSequence = ( 'name', 'value' )

class VarBindList(rfc1902.SequenceOf):
    protoComponent = VarBind()
    subtypeConstraints = ( subtypes.ValueSizeConstraint(0, max_bindings.get()), )

# Base class for a non-bulk PDU
class Pdu(rfc1902.Sequence):
    tagSet = rfc1902.Sequence.tagSet.clone(
        tagClass=tags.tagClassContext
        )
    # PDU structure
    protoComponents = { 'request_id': RequestId(),
                        'error_status': ErrorStatus(),
                        'error_index': ErrorIndex(),
                        'variable_bindings': VarBindList() }
    protoSequence = ( 'request_id', 'error_status',
                      'error_index', 'variable_bindings' )
    
class NonRepeaters(rfc1902.Integer):
    subtypeConstraints = ( subtypes.ValueRangeConstraint(0, max_bindings.get()), )

class MaxRepetitions(rfc1902.Integer):
    subtypeConstraints = ( subtypes.ValueRangeConstraint(0, max_bindings.get()), )
    initialValue = 255

# Base class for bulk PDU
class BulkPdu(rfc1902.Sequence):
    tagSet = rfc1902.Sequence.tagSet.clone(
        tagClass=tags.tagClassContext
        )
    # PDU structure
    protoComponents = { 'request_id': RequestId(),
                        'non_repeaters': NonRepeaters(),
                        'max_repetitions': MaxRepetitions(),
                        'variable_bindings': VarBindList() }
    protoSequence = ( 'request_id', 'non_repeaters',
                      'max_repetitions', 'variable_bindings' )

class GetRequestPdu(Pdu):
    tagSet = Pdu.tagSet.clone(tagId=0x00)

class GetNextRequestPdu(Pdu):
    tagSet = Pdu.tagSet.clone(tagId=0x01)

class ResponsePdu(Pdu):
    tagSet = Pdu.tagSet.clone(tagId=0x02)

class SetRequestPdu(Pdu):
    tagSet = Pdu.tagSet.clone(tagId=0x03)

class GetBulkRequestPdu(BulkPdu):
    tagSet = BulkPdu.tagSet.clone(tagId=0x05)

class InformRequestPdu(Pdu):
    tagSet = Pdu.tagSet.clone(tagId=0x06)

class SnmpV2TrapPdu(Pdu):
    tagSet = Pdu.tagSet.clone(tagId=0x07)

# XXX v1 compatible alias
TrapPdu = SnmpV2TrapPdu

class ReportPdu(Pdu):
    tagSet = Pdu.tagSet.clone(tagId=0x08)

class Pdus(rfc1902.Choice):
    protoComponents = { 'get_request': GetRequestPdu(),
                        'get_next_request': GetNextRequestPdu(),
                        'get_bulk_request': GetBulkRequestPdu(),
                        'response': ResponsePdu(),
                        'set_request': SetRequestPdu(),
                        'inform_request': InformRequestPdu(),
                        'snmpV2_trap': SnmpV2TrapPdu(),
                        'report': ReportPdu() }
    
class Message(rfc1902.Sequence):
    protoComponents = { 'version': Version(),
                        'community': Community(),
                        'pdu': Pdus() }
    protoSequence = ( 'version', 'community', 'pdu' )
