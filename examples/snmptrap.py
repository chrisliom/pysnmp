#!/usr/bin/env python
"""
   Send SNMP trap to remote SNMP manager.

   Since MIB parser is not yet implemented in Python, this script takes and
   reports Object IDs in dotted numeric representation only.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
import sys, getopt
from pysnmp.proto import v1, v2c
from pysnmp.mapping.udp import role
import pysnmp.proto.cli.ucd

# Initialize help messages
options =           'Options:\n'
options = options + '  -p <port>      port to communicate with at the agent. Default is 162.\n'
options = options + '  -v <version>   SNMP version to use [1, 2c]. Default is 1 (version one).\n'
usage = 'Usage: %s [options] <snmp-agent>' % sys.argv[0]
usage = usage + '\n' + options + ' ' + v2c.Trap().cliUcdGetUsage() + '\n' + \
        v1.Trap().cliUcdGetUsage()
    
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

# Choose protocol version specific module
try:
    snmp = eval('v' + version)

except (NameError, AttributeError):
    print 'Unsupported SNMP protocol version: %s\n%s' % (version, usage)
    sys.exit(-1)

if len(args) < 1:
    print 'Insufficient number of arguments supplied\n%s' % usage
    sys.exit(-1)

agent = args[0]

# Create SNMP Trap message
req = snmp.Trap()

# Initialize request message from C/L params
req.cliUcdSetArgs(args[1:])

# Create SNMP manager object
client = role.manager((agent, port))

# Encode SNMP request message and try to send it to SNMP manager
client.send(req.encode())

