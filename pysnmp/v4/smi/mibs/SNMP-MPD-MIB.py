# PySNMP SMI module. Autogenerated from smidump -f python SNMP-MPD-MIB
# by libsmi2pysnmp-0.0.7-alpha at Thu Nov 16 18:54:13 2006,
# Python version (2, 4, 3, 'final', 0)

# Imported just in case new ASN.1 types would be created
from pyasn1.type import constraint, namedval

# Imports

( Integer, ObjectIdentifier, OctetString, ) = mibBuilder.importSymbols("ASN1", "Integer", "ObjectIdentifier", "OctetString")
( ModuleCompliance, ObjectGroup, ) = mibBuilder.importSymbols("SNMPv2-CONF", "ModuleCompliance", "ObjectGroup")
( Bits, Counter32, Integer32, ModuleIdentity, MibIdentifier, MibScalar, MibTable, MibTableRow, MibTableColumn, TimeTicks, snmpModules, ) = mibBuilder.importSymbols("SNMPv2-SMI", "Bits", "Counter32", "Integer32", "ModuleIdentity", "MibIdentifier", "MibScalar", "MibTable", "MibTableRow", "MibTableColumn", "TimeTicks", "snmpModules")

# Objects

snmpMPDMIB = ModuleIdentity((1, 3, 6, 1, 6, 3, 11)).setRevisions(("2002-10-14 00:00","1999-05-04 16:36","1997-09-30 00:00",))
snmpMPDAdmin = MibIdentifier((1, 3, 6, 1, 6, 3, 11, 1))
snmpMPDMIBObjects = MibIdentifier((1, 3, 6, 1, 6, 3, 11, 2))
snmpMPDStats = MibIdentifier((1, 3, 6, 1, 6, 3, 11, 2, 1))
snmpUnknownSecurityModels = MibScalar((1, 3, 6, 1, 6, 3, 11, 2, 1, 1), Counter32()).setMaxAccess("readonly")
snmpInvalidMsgs = MibScalar((1, 3, 6, 1, 6, 3, 11, 2, 1, 2), Counter32()).setMaxAccess("readonly")
snmpUnknownPDUHandlers = MibScalar((1, 3, 6, 1, 6, 3, 11, 2, 1, 3), Counter32()).setMaxAccess("readonly")
snmpMPDMIBConformance = MibIdentifier((1, 3, 6, 1, 6, 3, 11, 3))
snmpMPDMIBCompliances = MibIdentifier((1, 3, 6, 1, 6, 3, 11, 3, 1))
snmpMPDMIBGroups = MibIdentifier((1, 3, 6, 1, 6, 3, 11, 3, 2))

# Augmentions

# Groups

snmpMPDGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 11, 3, 2, 1)).setObjects(("SNMP-MPD-MIB", "snmpInvalidMsgs"), ("SNMP-MPD-MIB", "snmpUnknownPDUHandlers"), ("SNMP-MPD-MIB", "snmpUnknownSecurityModels"), )

# Exports

# Module identity
mibBuilder.exportSymbols("SNMP-MPD-MIB", PYSNMP_MODULE_ID=snmpMPDMIB)

# Objects
mibBuilder.exportSymbols("SNMP-MPD-MIB", snmpMPDMIB=snmpMPDMIB, snmpMPDAdmin=snmpMPDAdmin, snmpMPDMIBObjects=snmpMPDMIBObjects, snmpMPDStats=snmpMPDStats, snmpUnknownSecurityModels=snmpUnknownSecurityModels, snmpInvalidMsgs=snmpInvalidMsgs, snmpUnknownPDUHandlers=snmpUnknownPDUHandlers, snmpMPDMIBConformance=snmpMPDMIBConformance, snmpMPDMIBCompliances=snmpMPDMIBCompliances, snmpMPDMIBGroups=snmpMPDMIBGroups)

# Groups
mibBuilder.exportSymbols("SNMP-MPD-MIB", snmpMPDGroup=snmpMPDGroup)
