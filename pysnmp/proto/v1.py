"""
   Compatibility API to SMI and SNMP for v.1 (RFC1155 & RFC1157). Do
   not use it in new projects.

   Copyright 1999-2004 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'GetRequest', 'GetNextRequest', 'SetRequest', 'Trap', \
            'GetResponse', 'Request' ]

from pysnmp.proto.rfc1155 import *
from pysnmp.proto import rfc1157, error

VarBind = rfc1157.VarBind
VarBindList = rfc1157.VarBindList

class MessageBase(rfc1157.Message):
    def __init__(self, **kwargs):
        # Compatibility stub: initialize PDU type
        apply(rfc1157.Message.__init__, [self], kwargs)
        
class GetRequest(MessageBase):
    def __init__(self, **kwargs):
        apply(MessageBase.__init__, [self], kwargs)
        self['pdu']['get_request'] = rfc1157.GetRequestPdu()
class GetNextRequest(MessageBase):
    def __init__(self, **kwargs):
        apply(MessageBase.__init__, [self], kwargs)
        self['pdu']['get_next_request'] = rfc1157.GetNextRequestPdu()
class SetRequest(MessageBase):
    def __init__(self, **kwargs):
        apply(MessageBase.__init__, [self], kwargs)
        self['pdu']['set_request'] =  rfc1157.SetRequestPdu()
class Trap(MessageBase):
    def __init__(self, **kwargs):
        apply(MessageBase.__init__, [self], kwargs)    
        self['pdu']['trap'] = rfc1157.TrapPdu()
class GetResponse(MessageBase):
    def __init__(self, **kwargs):
        apply(MessageBase.__init__, [self], kwargs)
        self['pdu']['get_response'] = rfc1157.GetResponsePdu()

# An alias to make it looking similar to v.2c
Response = GetResponse

# Requests demux
class Request(rfc1157.Message): pass
