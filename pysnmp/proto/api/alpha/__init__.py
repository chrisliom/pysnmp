"""
    SNMP framework for Python.

    The pysnmp.proto.api.alpha sub-package implements a high-level
    API to various SNMP messages.

   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
from pysnmp.proto.api.alpha import rfc1157, rfc1905
map(lambda x: x.mixIn(), [ rfc1157, rfc1905 ])
