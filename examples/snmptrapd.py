#!/usr/bin/env python
"""
   Receive SNMP trap messages from remote SNMP agents and print
   trap details to stdout.

   Since MIB parser is not yet implemented in Python, this script takes and
   reports Object IDs in dotted numeric representation only.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
import sys, getopt
from pysnmp.proto import v1, v2c
from pysnmp.mapping.udp import role
import pysnmp.proto.api.generic
from pysnmp.asn1 import error

# Initialize help messages
options =           'Options:\n'
options = options + '  -p <port>      port to listen for requests from managers. Default is 162.\n'
options = options + '  -R             report variables types on output.'
usage = 'Usage: %s [options] [local-interface] [community]\n' % sys.argv[0]
usage = usage + options
    
# Initialize defaults
port = 162; iface = ''; community = None; reportTypeFlag = None

# Parse possible options
try:
    (opts, args) = getopt.getopt(sys.argv[1:], 'hp:R',\
                                 ['help', 'port=', 'report-type'])
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

        if opt[0] == '-R' or opt[0] == '--report-type':
            reportTypeFlag = 1

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
server = role.agent((None, None), [(iface, port)])

# Listen for SNMP messages from remote SNMP agents
while 1:
    # Receive a request message
    (question, src) = server.receive()

    # Attempt to decode received message by either of known protocol engines
    for snmp in [ v2c, v1 ]:
        req = snmp.Trap()
        try:
            req.decode(question)

        except error.ValueConstraintError:
            continue
        
        break
    else:
        print 'Inbound message dropped: unknown protocol version'
        continue

    # Fetch Object ID's and associated values
    vars = req.apiGenGetPdu().apiGenGetVarBind()

    # Print it out
    print 'SNMP message from: ' + str(src)
    print req['version'], ', type: ', req['pdu'].keys()[0]
    try:
        print 'Enterprise OID: ', req.apiGenGetPdu().apiGenGetEnterprise()
    except AttributeError: pass
    try:
        print 'Trap agent: ', req.apiGenGetPdu().apiGenGetAgentAddr()
    except AttributeError: pass
    try:
        print 'Generic trap: ', req.apiGenGetPdu().apiGenGetGenericTrap()
    except AttributeError: pass
    try:
        print 'Specific trap: ', req.apiGenGetPdu().apiGenGetSpecificTrap()
    except AttributeError: pass
    try:
        print 'Time stamp (uptime): ', req.apiGenGetPdu().apiGenGetTimeStamp()
    except AttributeError: pass        
    for (oid, val) in vars:
        print oid, ' ---> ',
        if reportTypeFlag:
            print val
        else:
            print repr(val.getTerminal().get())

    # Verify community name if needed
    if community is not None and req.apiGenGetCommunity() != community:
        print 'WARNING: UNMATCHED COMMUNITY NAME: ', req.apiGenGetCommunity()
        continue
