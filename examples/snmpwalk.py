#!/usr/bin/env python
"""
   Retrieve a subtree of lexicographically greater Object IDs starting from
   user specifed SNMP Object ID from arbitrary SNMP agent.

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
options = options + '  -R             report variables types on output.\n'
options = options + '  -C <app-opts>  application specific options\n'
options = options + '                 p:  print the number of variables found\n'
options = options + '                 i:  include given OID in the search range\n'
options = options + '                 c:  do not check returned OIDs are increasing'
usage = 'Usage: %s [options] <snmp-agent>' % sys.argv[0]
usage = usage + ' ' + v2c.GetRequest().cliUcdGetUsage() + '\n' + options
    
# Initialize defaults
port = 161; retries = 5; timeout = 1; version = '1'
reportTypeFlag = prtNumFlag = inclOidFlag = None
chkIncOidFlag = 1

# Parse possible options
try:
    (opts, args) = getopt.getopt(sys.argv[1:], 'hp:r:t:v:RC:',\
                                 ['help', 'port=', 'retries=', \
                                  'timeout=', 'version=', 'report-type', \
                                  'app-opts'])
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

        if opt[0] == '-C' or opt[0] == '--app-opts':
            for c in list(opt[1]):
                if c == 'p': prtNumFlag = 1
                if c == 'i': inclOidFlag = 1
                if c == 'c': chkIncOidFlag = 0

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
client.timeout = timeout
client.retries = retries

# Choose protocol version specific module
try:
    snmp = eval('v' + version)

except (NameError, AttributeError):
    print 'Unsupported SNMP protocol version: %s\n%s' % (version, usage)
    sys.exit(-1)

# Create and initialize SNMP GET/GETNEXT request objects
getNextReq = snmp.GetNextRequest(); getNextReq.cliUcdSetArgs(args[1:])
if inclOidFlag:
    getReq = snmp.GetRequest(); getReq.cliUcdSetArgs(args[1:])

# Store tables headers
headVars = map(lambda x: x[0], getNextReq.apiGenGetPdu().apiGenGetVarBind())

# Create a response message framework
rsp = snmp.Response()

# A counter for printed vars
prtOidCount = 0

# Traverse agent MIB
while 1:
    # Verify against out-of-order messages
    def cb_fun(answer, src):
        # Decode message
        rsp.decode(answer)
        
        # Make sure response matches request
        if req.match(rsp):
            return 1

    # Switch from/to Get/GetNext reqs if requested
    if inclOidFlag:
        req = getReq
        inclOidFlag = None
    else:
        req = getNextReq
        
    # Encode SNMP request message and try to send it to SNMP agent and
    # receive a response
    (answer, src) = client.send_and_receive(req.encode(), (None, 0), cb_fun)

    # Fetch Object ID's and associated values
    vars = rsp.apiGenGetPdu().apiGenGetVarBind()

    # Error handling makes sense only when walking
    if req is getNextReq:
        # Check for remote SNMP agent failure
        if rsp.apiGenGetPdu().apiGenGetErrorStatus():
            errorIndex = rsp.apiGenGetPdu().apiGenGetErrorIndex() - 1
            # SNMP agent (v.1) reports 'no such name' when walk is over
            if rsp.apiGenGetPdu().apiGenGetErrorStatus() == 2:
                # One of the tables exceeded
                for l in vars, headVars:
                    if errorIndex < len(l):
                        del l[errorIndex]
                    else:
                        raise error.ProtoError('Vad ErrorIndex vs VarBind in %s' \
                                               % rsp)
            else:
                errorStatus = str(rsp['pdu'].values()[0]['error_status'])
                if errorIndex < len(vars):
                    raise error.ProtoError(errorStatus + ' at ' + \
                                           str(vars[errorIndex][0]))
                raise error.ProtoError(errorStatus)

        # Exclude completed var-binds
        while 1:
            for idx in range(len(headVars)):
                if not snmp.ObjectIdentifier(headVars[idx]).isaprefix(vars[idx][0])\
                       or isinstance(vars[idx][1], v2c.EndOfMibView):
                    # One of the tables exceeded
                    for l in vars, headVars:
                        del l[idx]
                    break
            else:
                break

        # Make sure OIDs are increasing
        if chkIncOidFlag:
            badOids = filter(lambda (x, y): x > y,
                             map(None,
                                 map(lambda x: x[0],
                                     req.apiGenGetPdu().apiGenGetVarBind()),
                                 map(lambda x: x[0],
                                     rsp.apiGenGetPdu().apiGenGetVarBind())))
            if len(badOids):
                print 'Error: OID not increasing: ', str(badOids)
                break

    if len(headVars) == 0:
        break

    # Print out results
    for (oid, val) in vars:
        print oid, ' ---> ',
        if reportTypeFlag:
            print val
        else:
            print repr(val.getTerminal().get())

        prtOidCount = prtOidCount + 1
    
    # Update request ID
    req.apiGenGetPdu()['request_id'].inc(1)

    # Load get-next'ed vars into new req
    req.apiGenGetPdu().apiGenSetVarBind(vars)

if prtNumFlag:
    print 'Variables found: %d' % prtOidCount
