"""
   Implementation of SMI and SNMP for v.1 (RFC1155 & RFC1157)

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'GetRequest', 'GetNextRequest', 'SetRequest', 'Trap', \
            'GetResponse', 'Request' ]

from pysnmp.proto.rfc1155 import *
from pysnmp.proto import rfc1157, error

# These do not require any additional subtyping
from pysnmp.proto.rfc1157 import VarBind, VarBindList

class _RequestPduSpecifics:
    """Not really a class but a mean to create a new scope to keep
       subtyped v.1 request specifics
    """
    class ErrorStatus(rfc1157.ErrorStatus):
        """Request-specific PDU error status
        """
        valueRangeConstraint = (0, 0)

    class ErrorIndex(rfc1157.ErrorIndex):
        """Request-specific PDU error index
        """
        valueRangeConstraint = (0, 0)

    def reply(self, **kwargs):
        """Build and return a response PDU from this request PDU
        """
        rsp = apply(GetResponse.Pdus.GetResponsePdu, [], kwargs)
        rsp['request_id'] = self['request_id']
        rsp['variable_bindings'] = self['variable_bindings']

        return rsp

    def match(self, rspPdu):
        """Return true if response PDU matches request PDU
        """
        if not isinstance(rspPdu, rfc1157.GetResponsePdu):
            raise error.BadArgumentError('Incompatible types for comparation %s with %s' % (self.__class__.__name__, str(rspPdu)))
        
        if self['request_id'] == rspPdu['request_id']:
            return 1
        
class _RequestSpecifics:
    """Request-specific methods
    """
    def reply(self, **kwargs):
        """Create v.1 GETRESPONSE message from this request message
        """
        rsp = apply(GetResponse, [], kwargs)
        rsp['community'] = self['community']

        pdu = self['pdu'].values()[0]
        if hasattr(pdu, 'reply'):
            rsp['pdu']['get_response'] = pdu.reply()

        return rsp

    def match(self, rsp):
        """Return true if response message matches this request message
        """
        if not isinstance(rsp, GetResponse):
            raise error.BadArgumentError('Incompatible types for comparation %s with %s' % (self.__class__.__name__, str(rsp)))

        # Make sure response matches request
        if self['community'] !=  rsp['community']:
            return
        return self['pdu'].values()[0].match(rsp['pdu'].values()[0])

# Get request

class GetRequest(rfc1157.Message, _RequestSpecifics):
    """Strictly typed v.1 GETREQUEST
    """
    class Pdus(rfc1157.Pdus):
        """GETREQUEST specific selection of applicible PDUs
        """
        class GetRequestPdu(rfc1157.GetRequestPdu,\
                            _RequestPduSpecifics):
            """Strictly typed v.1 GETREQUEST PDU class
            """
            fixedComponents = [ rfc1157.RequestId,\
                                _RequestPduSpecifics.ErrorStatus, \
                                _RequestPduSpecifics.ErrorIndex, \
                                VarBindList ]

        choiceNames = [ 'get_request' ]
        choiceComponents = [ GetRequestPdu ]
        initialComponent = choiceComponents[0]

    fixedComponents = [ rfc1157.Version, rfc1157.Community, Pdus ]

# GetNext request

class GetNextRequest(rfc1157.Message, _RequestSpecifics):
    """Strictly typed v.1 GETNEXTREQUEST
    """
    class Pdus(rfc1157.Pdus):
        """GETNEXTREQUEST specific selection of applicible PDUs
        """
        class GetNextRequestPdu(rfc1157.GetNextRequestPdu, \
                                _RequestPduSpecifics):
            """Strictly typed v.1 GETNEXTREQUEST PDU class
            """
            fixedComponents = [ rfc1157.RequestId,\
                                _RequestPduSpecifics.ErrorStatus, \
                                _RequestPduSpecifics.ErrorIndex, \
                                VarBindList ]

        choiceNames = [ 'get_next_request' ]
        choiceComponents = [ GetNextRequestPdu ]
        initialComponent = choiceComponents[0]

    fixedComponents = [ rfc1157.Version, rfc1157.Community, Pdus ]

# Set request

class SetRequest(rfc1157.Message, _RequestSpecifics):
    """Strictly typed v.1 SETREQUEST
    """
    class Community(rfc1157.Community):
        """SETREQUEST specific community name
        """
        initialValue = 'private'

    class Pdus(rfc1157.Pdus):
        """SETREQUEST specific selection of applicible PDUs
        """
        class SetRequestPdu(rfc1157.SetRequestPdu, _RequestPduSpecifics):
            """Strictly typed v.1 SETREQUEST PDU
            """
            fixedComponents = [ rfc1157.RequestId, \
                                _RequestPduSpecifics.ErrorStatus, \
                                _RequestPduSpecifics.ErrorIndex, \
                                VarBindList ]

        choiceNames = [ 'set_request' ]
        choiceComponents = [ SetRequestPdu ]
        initialComponent = choiceComponents[0]
    
    fixedComponents = [ rfc1157.Version, Community, Pdus ]

# Trap message

class Trap(rfc1157.Message):
    """Strictly typed v.1 TRAP request
    """
    class Pdus(rfc1157.Pdus):
        """TRAP request specific selection of applicible PDUs
        """
        class TrapPdu(rfc1157.TrapPdu):
            """Strictly typed v.1 TRAP request PDU class
            """
            fixedComponents = [ rfc1157.Enterprise, rfc1157.AgentAddr, \
                                rfc1157.GenericTrap, rfc1157.SpecificTrap, \
                                rfc1157.TimeStamp, VarBindList ]

        choiceNames = [ 'trap' ]
        choiceComponents = [ TrapPdu ]
        initialComponent = choiceComponents[0]

    fixedComponents = [ rfc1157.Version, rfc1157.Community, Pdus ]

# Get response

class GetResponse(rfc1157.Message):
    """Strictly typed v.1 GETRESPONSE
    """
    class Pdus(rfc1157.Pdus):
        """GETRSPONSE specific selection of applicible PDUs
        """
        class GetResponsePdu(rfc1157.GetResponsePdu):
            """Strictly typed v.1 GETRESPONSE PDU
            """
            fixedComponents = [ rfc1157.RequestId, rfc1157.ErrorStatus, \
                                rfc1157.ErrorIndex, VarBindList ]

        choiceNames = [ 'get_response' ]
        choiceComponents = [ GetResponsePdu ]
        initialComponent = choiceComponents[0]

    fixedNames = [ 'version', 'community', 'pdu' ]
    fixedComponents = [ rfc1157.Version, rfc1157.Community, Pdus ]

# An alias to make it looking similar to v.2c
Response = GetResponse

# Requests demux

class Request(rfc1157.Message, _RequestSpecifics):
    """Strictly typed any v.1 request
    """
    class Pdus(rfc1157.Pdus):
        """Request specific selection of applicible PDUs
        """
        choiceNames = [ 'get_request', 'get_next_request', \
                        'set_request' ]
        choiceComponents = [ GetRequest.Pdus.GetRequestPdu, \
                             GetNextRequest.Pdus.GetNextRequestPdu, \
                             SetRequest.Pdus.SetRequestPdu ]

    fixedComponents = [ rfc1157.Version, rfc1157.Community, Pdus ]
