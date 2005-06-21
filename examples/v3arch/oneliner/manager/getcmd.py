from pysnmp.entity.rfc3413.oneliner import cmdgen

errorIndication, errorStatus, errorIndex, varBinds = cmdgen.CmdGen().getCmd(
    cmdgen.CommunityData('test-agent', 'public'),
#    cmdgen.UsmUserData('test-user', 'authkey1', 'privkey1'),
    cmdgen.UdpTransportTarget(('localhost', 161)),
    (('sysDescr', 'SNMPv2-MIB'), 0),
    (('sysDescr',), 0),
    ('iso','org','dod','internet','mgmt','mib-2','system','sysDescr',0),
    (1,3,6,1,2,1,1,1,0)
    )

if errorIndication:
    print errorIndication
else:
    if errorStatus:
        print '%s at %s\n' % (errorStatus, varBinds[errorIndex-1])
    else:
        for varBind in varBinds:
            print '%s = %s' % varBind
