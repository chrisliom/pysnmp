#!/usr/local/bin/python -O
"""
   Set new values to MIB variables associated with user specifed
   SNMP Object IDs at arbitrary SNMP agent.

   Since MIB parser is not yet implemented in Python, this script takes and
   reports Object IDs in dotted numeric representation only.

   Written by Ilya Etingof <ilya@glas.net>, 2000-2002

"""
import sys
import getopt

# Import PySNMP modules
from pysnmp import asn1, v1, v2c
from pysnmp import role

# Initialize help messages
options =           'Options:\n'
options = options + '  -p <port>      port to communicate with at the agent. Default is 161.\n'
options = options + '  -r <retries>   number of retries to be used in requests. Default is 5.\n'
options = options + '  -t <timeout>   timeout between retries. Default is 1.\n'
options = options + '  -v <version>   SNMP version to use [1, 2c]. Default is 1 (version one).\n'
types =         'Types:\n'
types = types + '   i:            INTEGER\n'
types = types + '   u:            unsigned INTEGER\n'
types = types + '   t:            TIMETICKS\n'
types = types + '   a:            IPADDRESS\n'
types = types + '   o:            OBJID\n'
types = types + '   s:            STRING\n'
types = types + '   U:            COUNTER64 (version 2 and above)'
usage = 'Usage: %s [options] <snmp-agent> <community> <oid type val [...]>\n' % sys.argv[0]
usage = usage + options + types
    
# Initialize defaults
port = 161
retries = 5
timeout = 1
version = '1'
    
# Parse possible options
try:
    (opts, args) = getopt.getopt(sys.argv[1:], 'hp:r:t:v:',\
                                 ['help', 'port=', 'retries=', \
                                  'timeout=', 'version='])

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

        if opt[0] == '-r' or opt[0] == '--retries':
            retries = int(opt[1])

        if opt[0] == '-t' or opt[0] == '--timeout':
            timeout = int(opt[1])

        if opt[0] == '-v' or opt[0] == '--version':
            version = opt[1]

except ValueError, why:
    print 'Bad parameter \'%s\' for option %s: %s\n%s' \
          % (opt[1], opt[0], why, usage)
    sys.exit(-1)

if len(args) < 4:
    print 'Insufficient number of arguments supplied\n%s' % usage
    sys.exit(-1)

# Try to provide usage-level compatibility with UCD snmpset
varargs = []
idx = 2
while idx < len(args)-2:
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
client = role.manager((args[0], port))

# Pass it a few options
client.timeout = timeout
client.retries = retries

# Create a SNMP request&response objects from protocol version
# specific module.
try:
    req = eval('v' + version).SETREQUEST()
    rsp = eval('v' + version).GETRESPONSE()

except (NameError, AttributeError):
    print 'Unsupported SNMP protocol version: %s\n%s' % (version, usage)
    sys.exit(-1)

encoded_oids = []
encoded_vals = []

for (oid, type, val) in varargs:
    encoded_oids.append(asn1.OBJECTID().encode(oid))
    encoded_vals.append(eval('asn1.'+type+'()').encode(val))

# Encode OIDs along with their respective values, encode SNMP
# request message and try to send it to SNMP agent and receive
# a response
(answer, src) = client.send_and_receive( \
         req.encode(community=args[1], \
                    encoded_oids=encoded_oids, encoded_vals=encoded_vals))

# Decode SNMP response message
rsp.decode(answer)

# Make sure response matches request (request IDs, communities, etc)
if req != rsp:
    raise 'Unmatched response: %s vs %s' % (str(req), str(rsp))

# Decode BER encoded Object IDs.
oids = map(lambda x: x[0], map(asn1.OBJECTID().decode, \
                               rsp['encoded_oids']))

# Decode BER encoded values associated with Object IDs.
vals = map(lambda x: x[0](), map(asn1.decode, rsp['encoded_vals']))

# Check for remote SNMP agent failure
if rsp['error_status']:
    raise 'SNMP error #' + str(rsp['error_status']) + ' for OID #' \
          + str(rsp['error_index'])

for (oid, val) in map(None, oids, vals):
    print oid + ' ---> ' + str(val)
