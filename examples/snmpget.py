#!/usr/bin/env python
"""
   Retrieve MIB variables associated with user specifed SNMP Object IDs
   from arbitrary SNMP agent.

   Since MIB parser is not yet implemented in Python, this script takes and
   reports Object IDs in dotted numeric representation only.

   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
import sys, getopt
from pysnmp.proto import v1, v2c, error
from pysnmp.mapping.udp import role
import pysnmp.proto.api.generic
import pysnmp.proto.cli.ucd

# Initialize help messages
options =           'Options:\n'
options = options + '  -p <port>      port to communicate with at the agent. Default is 161.\n'
options = options + '  -r <retries>   number of retries to be used in requests. Default is 5.\n'
options = options + '  -t <timeout>   timeout between retries. Default is 1.\n'
options = options + '  -v <version>   SNMP version to use [1, 2c]. Default is 1 (version one).\n'
options = options + '  -R             report variables types on output.'
usage = 'Usage: %s [options] <snmp-agent>' % sys.argv[0]
usage = usage + ' ' + v2c.GetRequest().cliUcdGetUsage() + '\n' + options
    
# Initialize defaults
port = 161; retries = 5; timeout = 1; version = '1'; reportTypeFlag = None
    
# Parse possible options
try:
    (opts, args) = getopt.getopt(sys.argv[1:], 'hp:r:t:v:R',\
                                 ['help', 'port=', 'retries=', \
                                  'timeout=', 'version=', 'report-type'])

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

        if opt[0] == '-R' or opt[0] == '--report-type':
            reportTypeFlag = 1

except ValueError, why:
    print 'Bad parameter \'%s\' for option %s: %s\n%s' \
          % (opt[1], opt[0], why, usage)
    sys.exit(-1)

if len(args) < 1:
    print 'Insufficient number of arguments supplied\n%s' % usage
    sys.exit(-1)

# Create SNMP manager object
client = role.manager((args[0], port))

# Pass it a few options
client.timeout = timeout; client.retries = retries

# Choose protocol version specific module
try:
    snmp = eval('v' + version)
except (NameError, AttributeError):
    print 'Unsupported SNMP protocol version: %s\n%s' % (version, usage)
    sys.exit(-1)

# Create SNMP GET request
req = snmp.GetRequest()

# Initialize request message from C/L params
req.cliUcdSetArgs(args[1:])

# Create SNMP response message framework
rsp = snmp.Response()

def cb_fun(answer, src):
    """This is meant to verify inbound messages against out-of-order
       messages
    """
    # Decode message
    rsp.decode(answer)
        
    # Make sure response matches request
    if req.match(rsp):
        return 1

# Encode SNMP request message and try to send it to SNMP agent and
# receive a response
(answer, src) = client.send_and_receive(req.encode(), (None, 0), cb_fun)

# Fetch Object ID's and associated values
vars = rsp.apiGenGetPdu().apiGenGetVarBind()

# Check for remote SNMP agent failure
if rsp.apiGenGetPdu().apiGenGetErrorStatus():
    errorIndex = rsp.apiGenGetPdu().apiGenGetErrorIndex() - 1
    errorStatus = str(rsp['pdu'].values()[0]['error_status'])
    if errorIndex in range(len(vars)):
        raise error.ProtoError(errorStatus + ' at ' + str(vars[errorIndex][0]))
    raise error.ProtoError(errorStatus)
        
# Print out results
for (oid, val) in vars:
    print oid, ' ---> ',
    if reportTypeFlag:
        print val
    else:
        print repr(val.getTerminal().get())
