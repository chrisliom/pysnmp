"""
   UCD-SNMP-style command line interface to rfc1905 objects

   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ '' ]

import string
from pysnmp.proto.cli.ucd import rfc1157
from pysnmp.proto import rfc1905
from pysnmp.proto.cli import error

class VersionMixIn(rfc1157.VersionMixIn): pass
class CommunityMixIn(rfc1157.CommunityMixIn): pass
class RequestIdMixIn(rfc1157.RequestIdMixIn): pass
class ErrorStatusMixIn(rfc1157.ErrorStatusMixIn): pass
class ErrorIndexMixIn(rfc1157.ErrorIndexMixIn): pass
class VarBindListMixIn(rfc1157.VarBindListMixIn): pass

class NoSuchObjectMixIn:
    cliUcdOptId = None

class NoSuchInstanceMixIn:
    cliUcdOptId = None

class EndOfMibViewMixIn:
    cliUcdOptId = None

class NonRepeatersMixIn:
    cliUcdOptId = '-Cn:'
    cliUcdOptValName = 'non-repeaters'

class MaxRepetitionsMixIn:
    cliUcdOptId = '-Cr:'
    cliUcdOptValName = 'max-repetitions'

# Trap stuff

class SnmpV2TrapPduMixIn: pass
# XXX
#    def cliUcdSetArgs(self, argv):
    
def mixIn():
    """Register this module's mix-in classes at their bases
    """
    mixInComps = [ (rfc1905.Version, VersionMixIn),
                   (rfc1905.Community, CommunityMixIn),
                   (rfc1905.RequestId, RequestIdMixIn),
                   (rfc1905.ErrorStatus, ErrorStatusMixIn),
                   (rfc1905.ErrorIndex, ErrorIndexMixIn),
                   (rfc1905.VarBindList, VarBindListMixIn),
                   (rfc1905.NoSuchObject, NoSuchObjectMixIn),
                   (rfc1905.NoSuchInstance, NoSuchInstanceMixIn),
                   (rfc1905.EndOfMibView, EndOfMibViewMixIn),
                   (rfc1905.NonRepeaters, NonRepeatersMixIn),
                   (rfc1905.MaxRepetitions, MaxRepetitionsMixIn),
                   (rfc1905.SnmpV2TrapPdu, SnmpV2TrapPduMixIn) ]

    for (baseClass, mixIn) in mixInComps:
        if mixIn not in baseClass.__bases__:
            baseClass.__bases__ = (mixIn, ) + baseClass.__bases__
