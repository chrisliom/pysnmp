"""
   UCD-SNMP-style command line interface to rfc1157 objects

   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ '' ]

import string
from pysnmp.proto import rfc1157
from pysnmp.proto.cli import error

class VersionMixIn:
    cliUcdOptId = None

class CommunityMixIn:
    cliUcdOptId = '-c:'
    cliUcdOptValName = 'community'

class RequestIdMixIn:
    cliUcdOptId = None

class ErrorStatusMixIn:
    cliUcdOptId = None

class ErrorIndexMixIn:
    cliUcdOptId = None

class VarBindListMixIn:
    cliUcdOptBraces = ('<', '>')
    
# Trap stuff

class EnterpriseMixIn:
    cliUcdOptId = ''
    cliUcdOptValName = 'enterprise-OID'
    
class AgentAddrMixIn:
    class IpAddressMixIn:
        cliUcdOptId = ''

class GenericTrapMixIn:
    cliUcdOptId = ''
    cliUcdOptValName = 'trap-int-id'

class SpecificTrapMixIn:
    cliUcdOptId = ''
    cliUcdOptValName = 'trap-int-id'

class TimeStampMixIn:
    cliUcdOptId = ''

def mixIn():
    """Register this module's mix-in classes at their bases
    """
    mixInComps = [ (rfc1157.Version, VersionMixIn),
                   (rfc1157.Community, CommunityMixIn),
                   (rfc1157.RequestId, RequestIdMixIn),
                   (rfc1157.ErrorStatus, ErrorStatusMixIn),
                   (rfc1157.ErrorIndex, ErrorIndexMixIn),
                   (rfc1157.VarBindList, VarBindListMixIn),
                   (rfc1157.Enterprise, EnterpriseMixIn),
                   (rfc1157.AgentAddr.IpAddress, \
                    AgentAddrMixIn.IpAddressMixIn),
                   (rfc1157.GenericTrap, GenericTrapMixIn),
                   (rfc1157.SpecificTrap, SpecificTrapMixIn),
                   (rfc1157.TimeStamp, TimeStampMixIn) ]

    for (baseClass, mixIn) in mixInComps:
        if mixIn not in baseClass.__bases__:
            baseClass.__bases__ = (mixIn, ) + baseClass.__bases__
