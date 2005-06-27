# SNMP GETNEXT with MIB resolution
import string
from pysnmp.entity.rfc3413.oneliner import cmdgen

cmdGen = cmdgen.CmdGen()

errorIndication, errorStatus, errorIndex, \
                 varBinds, varBindTable = cmdGen.nextCmd(
    # SNMP v2
#    cmdgen.CommunityData('test-agent', 'public'),
    # SNMP v3
    cmdgen.UsmUserData('test-user', 'authkey1', 'privkey1'),
    cmdgen.UdpTransportTarget(('localhost', 161)),
    (1,3,6,1,2,1)
#    (('system',),)
    )

if errorIndication:
    print errorIndication
else:
    if errorStatus:
        print '%s at %s\n' % (errorStatus, varBinds[errorIndex-1])
    else:
        for varBindTableRow in varBindTable:
            for varBind in varBindTableRow:
                oid, val = varBind
                (symName, modName), indices = cmdgen.mibvar.oidToInstanceName(
                    cmdGen.mibViewController, oid
                    )
                print '%s::%s.%s = %s' % (
                    modName, symName, string.join(map(str, indices), '.'),
                    cmdgen.mibvar.cloneFromMibValue(cmdGen.mibViewController, modName, symName, val)
                    )
