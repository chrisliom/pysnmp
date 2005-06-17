from pysnmp.entity.rfc3413.oneliner import cmdgen

errorIndication, errorStatus, errorIndex, \
                 varBinds, varBindTable = cmdgen.CmdGen().nextCmd(
    cmdgen.UsmUserData('test-user', 'authkey1', 'privkey1'),
    cmdgen.UdpTransportTarget(('localhost', 161)),
    (('system',),)
    )

if errorIndication:
    print errorIndication
else:
    if errorStatus:
        print '%s at %s\n' % (errorStatus, varBinds[errorIndex-1])
    else:
        for varBindTableRow in varBindTable:
            for varBind in varBindTableRow:
                print '%s = %s' % varBind
