#!/usr/bin/env python
"""
   Retrieve a SNMP table of Object IDs starting from user specifed SNMP
   Object ID(s) from arbitrary SNMP agent using SNMP v.2 GETBULK PDU.

   Since MIB parser is not yet implemented in Python, this script takes and
   reports Object IDs in dotted numeric representation only.

   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
import sys, string, getopt
from pysnmp.proto import v2c, error
from pysnmp.mapping.udp import role
import pysnmp.proto.api.generic
import pysnmp.proto.cli.ucd

# Initialize help messages
options =           'Options:\n'
options = options + '  -p <port>      port to communicate with at the agent. Default is 161.\n'
options = options + '  -r <retries>   number of retries to be used in requests. Default is 5.\n'
options = options + '  -t <timeout>   timeout between retries. Default is 1.\n'
options = options + '  -R             report variables types on output.\n'
options = options + '  -C <app-opts>  application specific options\n'
options = options + '                 p:      print the number of variables found\n'
options = options + '                 i:      include given OID in the search range\n'
options = options + '                 c:      do not check returned OIDs are increasing\n'
options = options + '                 n<NUM>: set non-repeaters to <NUM>\n'
options = options + '                 r<NUM>: set max-repeaters to <NUM>'
usage = 'Usage: %s [options] <snmp-agent>' % sys.argv[0]
usage = usage + ' ' + v2c.GetBulkRequest().cliUcdGetUsage() + '\n' + options
    
# Initialize defaults
port = 161; retries = 5; timeout = 1; reportTypeFlag = None
reportTypeFlag = prtNumFlag = inclOidFlag = None
nonRepeaters = 0; maxRepeaters = 10
chkIncOidFlag = 1

# Parse possible options
try:
    (opts, args) = getopt.getopt(sys.argv[1:], 'hp:r:t:RC:',\
                                 ['help', 'port=', 'retries=',\
                                  'timeout=', 'report-type',\
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

        if opt[0] == '-R' or opt[0] == '--report-type':
            reportTypeFlag = 1

        if opt[0] == '-C' or opt[0] == '--app-opts':
            i = 0
            while i < len(opt[1]):
                if opt[1][i] == 'p': prtNumFlag = 1
                if opt[1][i] == 'i': inclOidFlag = 1
                if opt[1][i] == 'c': chkIncOidFlag = 0
                if opt[1][i] in [ 'r', 'n' ]:
                    j = i + 1
                    while j < len(opt[1]) and opt[1][j] in string.digits:
                        j = j + 1
                    try:
                        n = string.atoi(opt[1][i+1:j])
                    except ValueError, why:
                        print 'Non/max repeaters parse error %s: %s' % \
                              (opt[1][i:j], why)
                        sys.exit(-1)
                    if opt[1][i] == 'r':
                        nonRepeaters = n
                    else:
                        maxRepeaters = n
                    i = j
                    continue
                i = i + 1
                
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

# Create SNMP GETBULK request
getBulkReq = v2c.GetBulkRequest(); getBulkReq.cliUcdSetArgs(args[1:])
if inclOidFlag:
    getReq = v2c.GetRequest(); getReq.cliUcdSetArgs(args[1:])

# Store tables headers
headVars = map(lambda x: x[0], getBulkReq.apiGenGetPdu().apiGenGetVarBind())

# Create a response message framework
rsp = v2c.Response()

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

    # Switch from/to Get/GetBulk reqs if requested
    if inclOidFlag:
        req = getReq
        inclOidFlag = None
    else:
        req = getBulkReq
        
    # Encode SNMP request message and try to send it to SNMP agent and
    # receive a response
    (answer, src) = client.send_and_receive(req.encode(), (None, 0), cb_fun)
    
    # Fetch Object ID's and associated values
    vars = rsp.apiGenGetPdu().apiGenGetVarBind()


    # Error handling makes sense only when walking
    if req is getBulkReq:
        # Check for remote SNMP agent failure
        if rsp.apiGenGetPdu().apiGenGetErrorStatus():
            errorIndex = rsp.apiGenGetPdu().apiGenGetErrorIndex() - 1
            errorStatus = str(rsp['pdu'].values()[0]['error_status'])
            if errorIndex < len(vars):
                raise error.ProtoError(errorStatus + ' at ' + \
                                       str(vars[errorIndex][0]))
            raise error.ProtoError(errorStatus)

        # The following is taken from RFC1905 (fixed not to depend of repetitions)
        N = 0;
        R = len(req.apiGenGetPdu().apiGenGetVarBind()) - N
        M = len(rsp.apiGenGetPdu().apiGenGetVarBind()) / R
        for i in range(1, M+1):
            for r in range(1, R+1):
                idx = N + ((i-1)*R) + r
                (oid, val) = vars[idx-1]
                if not v2c.ObjectIdentifier(headVars[r-1]).isaprefix(oid):
                    continue
                print oid, ' ---> ',
                if reportTypeFlag:
                    print val
                else:
                    print repr(val.getTerminal().get())
                prtOidCount = prtOidCount + 1

        # Leave the last of each requested OIDs
        vars = vars[-R:]

        # Exclude completed OIDs
        while 1:
            for idx in range(len(vars)):
                if not v2c.ObjectIdentifier(headVars[idx]).isaprefix(vars[idx][0]) \
                       or isinstance(vars[idx][1], v2c.EndOfMibView):
                    del vars[idx]; del headVars[idx]
                    break
            else:
                break
            
        # Make sure OIDs are increasing
        if chkIncOidFlag:
            bOids = filter(lambda (x, y): \
                           snmp.ObjectIdentifier(x) > snmp.ObjectIdentifier(y),
                           map(None, \
                               map(lambda x: x[0], vars), \
                               map(lambda x: x[0], \
                                   rsp.apiGenGetPdu().apiGenGetVarBind())))
            if len(bOids):
                print 'Error: OID not increasing: ', str(bOids)
                sys.exit(-1)
    else:
        for (oid, val) in vars:
            print oid, ' ---> ',
            if reportTypeFlag:
                print val
            else:
                print repr(val.getTerminal().get())
            prtOidCount = prtOidCount + 1
        
    if len(headVars) == 0:
        break
        
    # Update request ID
    req.apiGenGetPdu()['request_id'].inc(1)

    # Load get-next'ed vars into new req
    req.apiGenGetPdu().apiGenSetVarBind(vars)

if prtNumFlag:
    print 'Variables found: %d' % prtOidCount
