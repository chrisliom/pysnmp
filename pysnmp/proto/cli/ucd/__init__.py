"""
   SNMP framework for Python.

   The pysnmp.proto.cli.ucd sub-package implements a UCD-SNMP-style command
   line interface to SNMP message objects.

   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE
   for details.
"""
from pysnmp.proto.api import generic
from pysnmp.proto.cli.ucd import v1, v2c, rfc1157, rfc1905

# Mix-in all UCD CLI classes to their bases
for mod in [ rfc1157, rfc1905, v1, v2c]: mod.mixIn()
