"""
    SNMP framework for Python.

    The pysnmp.asn1.encoding.ber sub-package implements Basic Encoding
    Rules (BER) serialization method for ASN.1 objects.

   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE for details.
"""
from pysnmp.asn1.encoding.ber import univ

# Mix-in BER classes to their bases
univ.mixIn()
