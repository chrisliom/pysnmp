"""
   SNMP framework for Python.

   The pysnmp.mapping.udp.cli.ucd sub-package implements UCD-SNMP-style command
   line interface (CLI) to transport objects.
   
   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE
   for details.
"""
from pysnmp.mapping.udp.cli.ucd import role
map(lambda x: x.mixIn(), [ role ])

