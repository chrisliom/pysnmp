#!/usr/bin/env python
"""
   Perform SNMP GET request for user specified MIB variables against
   multiple SNNP agents at once.
   
   Since MIB parser is not yet implemented in Python, this script takes and
   reports Object IDs in dotted numeric representation only.

   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
import sys, getopt
from string import split
from pysnmp.error import PySnmpError
from pysnmp.proto import v1, v2c, error
from pysnmp.mapping.udp import bulkrole
import pysnmp.proto.api.generic
import pysnmp.proto.cli.ucd

def ParseOptions(argv):
    """Parse argv into options
    """
    # Initialize help messages
    options =           'Options:\n'
    options = options + '  -p <port>      port to communicate with at the agent. Default is 161.\n'
    options = options + '  -r <retries>   number of retries to be used in requests. Default is 5.\n'
    options = options + '  -t <timeout>   timeout between retries. Default is 1.\n'
    options = options + '  -v <version>   SNMP version to use [1, 2c]. Default is 1 (version one).\n'
    options = options + '  -i <filename>  file to read additional args from. Use \'stdin\' for stdin.\n'
    options = options + '  -R             report variables types on output.'
    usage = 'Usage: %s [options] <snmp-agent>' % sys.argv[0]
    usage = usage + ' ' + v2c.GetRequest().cliUcdGetUsage() + '\n' + options

    # Initialize defaults
    port = 161; retries = 5; timeout = 1; version = '1';
    input = None; reportTypeFlag = None

    # Parse possible options
    try:
        (opts, args) = getopt.getopt(argv, 'hp:r:t:v:i:R',\
                                     ['help', 'port=', 'retries=', \
                                      'timeout=', 'version=', 'input=',\
                                      'report-type'])

    except getopt.error, why:
        raise 'UsageError', 'getopt error: %s\n%s' % (why, usage)

    try:
        for opt in opts:
            if opt[0] == '-h' or opt[0] == '--help':
                raise 'UsageError', usage

            if opt[0] == '-p' or opt[0] == '--port':
                port = int(opt[1])

            if opt[0] == '-r' or opt[0] == '--retries':
                retries = int(opt[1])

            if opt[0] == '-t' or opt[0] == '--timeout':
                timeout = int(opt[1])

            if opt[0] == '-v' or opt[0] == '--version':
                version = opt[1]

            if opt[0] == '-i' or opt[0] == '--input':
                input = opt[1]

            if opt[0] == '-R' or opt[0] == '--report-type':
                reportTypeFlag = 1

    except ValueError, why:
        raise 'UsageError', 'Bad parameter \'%s\' for option %s: %s\n%s' \
              % (opt[1], opt[0], why, usage)

    if args and len(args) < 3:
        raise 'UsageError', \
              'Insufficient number of arguments supplied\n%s' % usage

    if not args and not input:
        raise 'UsageError', \
              'Neither command line nor file arguments supplied\n%s' % usage

    return (port, retries, timeout, version, input, reportTypeFlag, args)

def RunTarget(args):
    """Run request from a single line of args
    """
    (port, retries, timeout, version, input, reportTypeFlag, args) = \
           ParseOptions(args)

    # Pass options to manager
    client.timeout = timeout
    client.retries = retries
    
    # Build SNMP request and submit it to bulk transport from command line args
    if args:
        try:
            snmp = eval('v' + version)

        except (NameError, AttributeError):
            raise 'UsageError', \
                  'Unsupported SNMP protocol version: %s' % version

        # Create SNMP GET request
        req = snmp.GetRequest()

        # Initialize request message from C/L params
        req.cliUcdSetArgs(args[1:])
        
        # Store the reportTypeFlag param in request object whenever
        # possible XXX
        if not hasattr(req, 'reportTypeFlag'):
            req.reportTypeFlag = reportTypeFlag
 
        client.append(((args[0], port), req.encode(), req))

    # Read additional args from file
    if input:
        # Can also read from stdin
        if input == 'stdin':
            f = sys.stdin
        else:
            try:
                f = open(input)

            except IOError, why:
                raise 'RuntimeError', 'open() failed: %s' % why

        linenum = 0
        
        while 1:
            line = f.readline()

            if not line:
                break

            linenum = linenum + 1
            
            args = split(line)
            
            if len(args) < 3:
                raise 'UsageError', \
                      'Insufficient number of arguments at %s:%d: %s'\
                      % (input, linenum, args)

            try:
                RunTarget(args)

            except 'UsageError', why:
                raise 'UsageError', 'at line %s:%d: %s' % (input, linenum, why)
    
# Create bulk SNMP manager object
client = bulkrole.manager()

try:
    RunTarget(sys.argv[1:])

except 'UsageError', why:
    print why
    sys.exit(-1)
    
# Run the I/O
client.dispatch()

# Walk over the list of replies
for (src, answer, req) in client:
    # Handle failed responses
    print 'Response from: ' + str(src)
    if answer is None:
        print 'Timed out...'
        continue

    if isinstance(answer, PySnmpError):
        print answer
        continue
    
    # Decode SNMP response
    rsp = req.reply(); rsp.decode(answer)

    # Make sure response matches request
    if not req.match(rsp):
        print 'Unmatched response: %s vs %s' % (req, rsp)
        continue
    
    # Fetch Object ID's and associated values
    vars = rsp.apiGenGetPdu().apiGenGetVarBind()

    # Check for remote SNMP agent failure
    if rsp.apiGenGetPdu().apiGenGetErrorStatus():
        errorIndex = rsp.apiGenGetPdu().apiGenGetErrorIndex() - 1
        errorStatus = str(rsp['pdu'].values()[0]['error_status'])
        if errorIndex < len(vars):
            raise error.ProtoError(errorStatus + ' at ' + str(vars[errorIndex][0]))
        raise error.ProtoError(errorStatus)
        
    # Print out results
    for (oid, val) in vars:
        print oid, ' ---> ',
        if hasattr(req, 'reportTypeFlag') and req.reportTypeFlag:
            print val
        else:
            print repr(val.getTerminal().get())
