#!/usr/local/bin/python -O
"""
   Receive SNMP trap messages from remote SNMP agents and print
   trap details to stdout.

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
options = options + '  -p <port>      port to listen for requests from managers. Default is 162.\n'
usage = 'Usage: %s [options] [local-interface] [community]\n' % sys.argv[0]
usage = usage + options
    
# Initialize defaults
port = 162
iface = ''
community = None

# Parse possible options
try:
    (opts, args) = getopt.getopt(sys.argv[1:], 'hp:',\
                                 ['help', 'port='])
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

except ValueError, why:
    print 'Bad parameter \'%s\' for option %s: %s\n%s' \
          % (opt[1], opt[0], why, usage)
    sys.exit(-1)

# Parse optional arguments
if len(args) > 0:
    iface = args[0]
if len(args) > 1:
    community = args[1]
    
# Create SNMP agent object
server = role.agent([(iface, port)])

# Listen for SNMP messages from remote SNMP managers
while 1:
    # Receive a request message
    (question, src) = server.receive()

    # Decode request of any version
    (req, rest) = v2c.decode(question)

    # Decode BER encoded Object IDs.
    oids = map(lambda x: x[0], map(asn1.OBJECTID().decode, \
                                   req['encoded_oids']))

    # Decode BER encoded values associated with Object IDs.
    vals = map(lambda x: x[0](), map(asn1.decode, req['encoded_vals']))
    
    # Print it out
    print 'SNMP message from: ' + str(src)
    print 'Version: ' + str(req['version']+1) + ', type: ' + str(req['tag'])
    if req['version'] == 0:
        print 'Enterprise OID: ' + str(req['enterprise'])
        print 'Trap agent: ' + str(req['agent_addr'])
        for t in v1.GENERIC_TRAP_TYPES.keys():
            if req['generic_trap'] == v1.GENERIC_TRAP_TYPES[t]:
                print 'Generic trap: %s (%d)' % (t, req['generic_trap'])
                break
        else:
            print 'Generic trap: ' + str(req['generic_trap'])
        print 'Specific trap: ' + str(req['specific_trap'])
        print 'Time stamp (uptime): ' + str(req['time_stamp'])
    for (oid, val) in map(None, oids, vals):
        print oid + ' ---> ' + str(val)

    # Verify community name if needed
    if community is not None and req['community'] != community:
        print 'WARNING: UNMATCHED COMMUNITY NAME: ' + str(community)
        continue
