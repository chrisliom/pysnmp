"""
   UCD-SNMP-style command line interface to rfc1902 objects

   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'IpAddressMixIn' ]

import string
from pysnmp.error import PySnmpError
from pysnmp.proto import rfc1902
from pysnmp.proto.cli.ucd import rfc1155
from pysnmp.proto.cli import error

class Counter32MixIn:
    cliUcdOptId = 'c32:'
    cliUcdOptValName = 'counter32'

class Gauge32MixIn:
    cliUcdOptId = 'g32:'
    cliUcdOptValName = 'gauge32'

class Counter64MixIn:
    cliUcdOptId = 'c64:'
    cliUcdOptValName = 'counter64'

class ObjectNameMixIn(rfc1155.ObjectNameMixIn): pass
    
def mixIn():
    """Register this module's mix-in classes at their bases
    """
    mixInComps = [ (rfc1902.Counter32, Counter32MixIn),
                   (rfc1902.Gauge32, Gauge32MixIn),
                   (rfc1902.Counter64, Counter64MixIn),
                   (rfc1902.ObjectName, ObjectNameMixIn) ]

    for (baseClass, mixIn) in mixInComps:
        if mixIn not in baseClass.__bases__:
            baseClass.__bases__ = (mixIn, ) + baseClass.__bases__

