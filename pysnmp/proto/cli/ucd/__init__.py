"""
   SNMP framework for Python.

   The pysnmp.proto.cli.ucd sub-package implements a UCD-SNMP-style command
   line interface to SNMP message objects.

   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE
   for details.
"""
from pysnmp.proto.cli.ucd import rfc1155, rfc1157, rfc1902, rfc1905
map(lambda x: x.mixIn(), [ rfc1155, rfc1157, rfc1902, rfc1905 ])
