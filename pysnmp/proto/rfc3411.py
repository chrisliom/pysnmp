"""
   An Architecture for Describing SNMP Management Frameworks (RFC3411).

   Written by Ilya Etingof <ilya@glas.net>, 2002.
"""
# Module public names
__all__ = [ 'GetRequestPdu', 'GetNextRequestPdu', 'ResponsePdu', \
            'SetRequestPdu', 'GetBulkRequestPdu', 'InformRequestPdu', \
            'SnmpV2TrapPdu', 'ReportPdu', 'ReadClass', 'WriteClass',
            'ResponseClass', 'NotificationClass', 'InternalClass',
            'ConfirmedClass', 'UnconfirmedClass' ]

from pysnmp.proto import rfc1905

# Functional PDU classification

class ReadClass:
    """Protocol operations that retrieve management information
    """
    pass

class WriteClass:
    """Protocol operations which attempt to modify management information
    """
    pass

class ResponseClass:
    """Protocol operations which are sent in response to a previous request
    """
    pass

class NotificationClass:
    """Protocol operations which send a notification to a notification
       receiver application.
    """
    pass

class InternalClass:
    """Protocol operations which are exchanged internally between
       SNMP engines.
    """
    pass

# PDU classification based on whether a response is expected

class ConfirmedClass:
    """Protocol operations which cause the receiving SNMP engine
       to send back a response.
    """
    pass

class UnconfirmedClass:
    """Protocol operations which are not acknowledged
    """
    pass

# Classify RFC1905 PDU types

class GetRequestPdu(rfc1905.GetRequestPdu, ReadClass, ConfirmedClass):
    pass

class GetNextRequestPdu(rfc1905.GetNextRequestPdu, ReadClass, ConfirmedClass):
    pass

class GetBulkRequestPdu(rfc1905.GetBulkRequestPdu, ReadClass, ConfirmedClass):
    pass

class SetRequestPdu(rfc1905.GetRequestPdu, WriteClass, ConfirmedClass):
    pass

class ResponsePdu(rfc1905.ResponsePdu, ResponseClass, UnconfirmedClass):
    pass

class ReportPdu(rfc1905.ReportPdu, ResponseClass, UnconfirmedClass):
    pass

class SnmpV2TrapPdu(rfc1905.SnmpV2TrapPdu, NotificationClass,
                    UnconfirmedClass):
    pass

class InformRequestPdu(rfc1905.InformRequestPdu, NotificationClass,
                       ConfirmedClass):
    pass

class ReportPdu(rfc1905.ReportPdu, InternalClass, UnconfirmedClass):
    pass
