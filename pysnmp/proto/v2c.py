"""Implementation of SMI and SNMP for v.2c (RFC1902 & RFC1905)"""
__all__ = [ 'GetRequest', 'GetNextRequest', 'SetRequest', 'Response', \
            'GetBulkRequest', 'InformRequest', 'Report', 'SnmpV2Trap',
            'Request' ]

from pysnmp.asn1 import subtypes
from pysnmp.proto.rfc1902 import *
from pysnmp.proto import rfc1905, error

# These do not require any additional subtyping
from rfc1905 import BindValue, VarBind, VarBindList, NoSuchObject, \
     NoSuchInstance, EndOfMibView

class MessageBase(rfc1905.Message):
    def __init__(self, **kwargs):
        # Compatibility stub: initialize PDU type
        apply(rfc1905.Message.__init__, [self], kwargs)
        
class GetRequest(MessageBase):
    def __init__(self, **kwargs):
        apply(MessageBase.__init__, [self], kwargs)
        self['pdu']['get_request'] = rfc1905.GetRequestPdu()
class GetNextRequest(MessageBase):
    def __init__(self, **kwargs):
        apply(MessageBase.__init__, [self], kwargs)
        self['pdu']['get_next_request'] = rfc1905.GetNextRequestPdu()
class SetRequest(MessageBase):
    def __init__(self, **kwargs):
        apply(MessageBase.__init__, [self], kwargs)
        self['pdu']['set_request'] =  rfc1905.SetRequestPdu()
class Trap(MessageBase):
    def __init__(self, **kwargs):
        apply(MessageBase.__init__, [self], kwargs)    
        self['pdu']['trap'] = rfc1905.TrapPdu()
class InformRequest(MessageBase):
    def __init__(self, **kwargs):
        apply(MessageBase.__init__, [self], kwargs)
        self['pdu']['inform_request'] = rfc1905.InformRequestPdu()
class SnmpV2Trap(MessageBase):
    def __init__(self, **kwargs):
        apply(MessageBase.__init__, [self], kwargs)
        self['pdu']['snmpV2_trap'] = rfc1905.SnmpV2TrapPdu()

# An alias to make it looking similar to v.1
Trap = SnmpV2Trap

class Report(MessageBase):
    def __init__(self, **kwargs):
        apply(MessageBase.__init__, [self], kwargs)
        self['pdu']['report'] = rfc1905.ReportPdu()
class GetBulkRequest(MessageBase):
    def __init__(self, **kwargs):
        apply(MessageBase.__init__, [self], kwargs)
        self['pdu']['get_bulk_request'] = rfc1905.GetBulkRequestPdu()

class Response(MessageBase):
    def __init__(self, **kwargs):
        apply(MessageBase.__init__, [self], kwargs)
        self['pdu']['response'] = rfc1905.ResponsePdu()

# An alias to make it looking similar to v.1
GetResponse = Response

# Requests demux
class Request(rfc1905.Message): pass
