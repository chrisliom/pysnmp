#!/usr/local/bin/python -O
"""
   Send SNMP trap to remote SNMP agent.

   Since MIB parser is not yet implemented in Python, this script takes and
   reports Object IDs in dotted numeric representation only.

   Written by Ilya Etingof <ilya@glas.net>, 2000-2002

"""
import sys
import time
import getopt

# Import PySNMP modules
from pysnmp import asn1, v1, v2c
from pysnmp import role

# Initialize help messages
options =           'Options:\n'
options = options + '  -p <port>      port to communicate with at the agent. Default is 162.\n'
options = options + '  -v <version>   SNMP version to use [1, 2c]. Default is 1 (version one).\n'
types =         'Types:\n'
types = types + '   i:            INTEGER\n'
types = types + '   u:            unsigned INTEGER\n'
types = types + '   t:            TIMETICKS\n'
types = types + '   a:            IPADDRESS\n'
types = types + '   o:            OBJID\n'
types = types + '   s:            STRING\n'
types = types + '   U:            COUNTER64 (version 2 and above)'
usage = 'Usage: %s [options] <snmp-agent> <community> [<trap-parameters>]\n' % sys.argv[0]
trapopt =           '-v 1 trap parameters:\n'
trapopt = trapopt + '   enterprise-oid agent trap-type specific-type uptime [oid <type val> [...]]>\n'
trapopt = trapopt + '-v 2c trap parameters:\n'
trapopt = trapopt + '   uptime trap-oid [oid <type val> [...]]>\n'
usage = usage + options + trapopt + types
    
# Initialize defaults
port = 161
version = '1'
    
# Parse possible options
try:
    (opts, args) = getopt.getopt(sys.argv[1:], 'hp:v:',\
                                 ['help', 'port=', 'version='])
except getopt.error, why:
    print 'getopt error: %s\n%s' % (why, usage)
    sys.exit(-1)

try:
    for opt in opts:
        if opt[0] == '-h' or opt[0] == '--help':
            print usage
            sys.exit(0)
        
        if opt[0] == '-p' or opt[0] == '--port':
            port = int(opt[1])

        if opt[0] == '-v' or opt[0] == '--version':
            version = opt[1]

except ValueError, why:
    print 'Bad parameter \'%s\' for option %s: %s\n%s' \
          % (opt[1], opt[0], why, usage)
    sys.exit(-1)

# v.1 trap params and v.1/v.2 vars repositories
targs = {}
varargs = []

if len(args) < 2:
    print 'Insufficient number of arguments supplied\n%s' % usage
    sys.exit(-1)

agent = args[0]
targs['community'] = args[1]

if version == '1':
    if len(args) > 2 and args[2]:
        targs['enterprise'] = args[2]
    else:
        targs['enterprise'] = '1.3.6.1.4.1.3.1.1'
    if len(args) > 3 and args[3]:
        targs['agent_addr'] = args[3]
    else:
        import socket
        targs['agent_addr'] = socket.gethostbyname(socket.gethostname())
    if len(args) > 4 and args[4]:
        targs['generic_trap'] = int(args[4])
    if len(args) > 5 and args[5]:
        targs['specific_trap'] = int(args[5])
    if len(args) > 6 and args[6]:
        targs['time_stamp'] = int(args[6])
    args = args[7:]

elif version == '2c':
    # Our uptime
    if len(args) > 2 and args[2]:
        varargs.append(('.1.3.6.1.2.1.1.3.0', 'TIMETICKS', int(args[2])))
    else:
        varargs.append(('.1.3.6.1.2.1.1.3.0', 'TIMETICKS', int(time.time())))
    # TrapOID
    if len(args) > 3 and args[3]:
        varargs.append(('.1.3.6.1.6.3.1.1.4.1.0', 'OBJECTID', args[3]))
    else:
        varargs.append(('.1.3.6.1.6.3.1.1.4.1.0', 'OBJECTID', \
                        '1.3.6.1.4.1.3.1.1'))
    args = args[4:]

else:
    print 'Unsupported SNMP protocol version: %s\n%s' % (version, usage)
    sys.exit(-1)

# Try to provide usage-level compatibility with UCD snmpset
idx = 0
while idx < len(args):
    try:
        if args[idx+1] == 'i':
            varargs.append((args[idx], 'INTEGER', int(args[idx+2])))
        elif args[idx+1] == 'u':
            varargs.append((args[idx], 'UNSIGNED32', int(args[idx+2])))
        elif args[idx+1] == 't':
            varargs.append((args[idx], 'TIMETICKS', int(args[idx+2])))
        elif args[idx+1] == 'a':
            varargs.append((args[idx], 'IPADDRESS', args[idx+2]))
        elif args[idx+1] == 'o':
            varargs.append((args[idx], 'OBJECTID', args[idx+2]))
        elif args[idx+1] == 's':
            varargs.append((args[idx], 'OCTETSTRING', args[idx+2]))
        elif args[idx+1] == 'U':
            varargs.append((args[idx], 'COUNTER64', long(args[idx+2])))
        else:
            print 'Unknown value type \'%s\'\n%s' % (args[idx+1], usage)
            sys.exit(-1)

        idx = idx + 3
            
    except IndexError:
        print 'Wrong number of arguments supplied\n%s' % usage
        sys.exit(-1)

    except (TypeError, ValueError), why:
        print 'Wrong type of value \'%s\': %s' % (args[idx+2], why)
        sys.exit(-1)

# Create SNMP manager object
client = role.manager((agent, port))

# Create a SNMP request object from protocol version specific module.
try:
    req = eval('v' + version).TRAPREQUEST()

except (NameError, AttributeError):
    raise 'Unsupported SNMP protocol version: ' + str(version)

# Load trap params
req.update(targs)

encoded_oids = []
encoded_vals = []

for (oid, type, val) in varargs:
    encoded_oids.append(asn1.OBJECTID().encode(oid))
    encoded_vals.append(eval('asn1.'+type+'()').encode(val))

# Encode OIDs along with their respective values, encode SNMP
# trap message and try to send it to SNMP agent
client.send(req.encode(encoded_oids=encoded_oids, \
                       encoded_vals=encoded_vals))
