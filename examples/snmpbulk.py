#!/usr/local/bin/python -O
"""
   Perform SNMP GET request for user specified MIB variables against
   multiple SNNP agents at once.
   
   Since MIB parser is not yet implemented in Python, this script takes and
   reports Object IDs in dotted numeric representation only.

   Written by Ilya Etingof <ilya@glas.net>, 2000-2002. 

"""
import sys
import string
import getopt

# Import PySNMP modules
from pysnmp import asn1, v1, v2c
from pysnmp import bulkrole

# Initialize help messages
options =           'Options:\n'
options = options + '  -p <port>      port to communicate with at the agent. Default is 161.\n'
options = options + '  -r <retries>   number of retries to be used in requests. Default is 5.\n'
options = options + '  -t <timeout>   timeout between retries. Default is 1.\n'
options = options + '  -v <version>   SNMP version to use [1, 2c]. Default is 1 (version one).\n'
options = options + '  -i <filename>  file to read additional args from. Use \'stdin\' for stdin.'
usage = 'Usage: %s [options] <snmp-agent> <community> <obj-id [[obj-id] ... ]\n' % sys.argv[0]
usage = usage + options
    
# Initialize defaults
port = 161
retries = 5
timeout = 1
version = '1'
input = None

# Parse possible options
try:
    (opts, args) = getopt.getopt(sys.argv[1:], 'hp:r:t:v:i:',\
                                 ['help', 'port=', 'retries=', \
                                  'timeout=', 'version=', 'input='])

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

        if opt[0] == '-i' or opt[0] == '--input':
            input = opt[1]

except ValueError, why:
    print 'Bad parameter \'%s\' for option %s: %s\n%s' \
          % (opt[1], opt[0], why, usage)
    sys.exit(-1)

if args and len(args) < 3:
    print 'Insufficient number of arguments supplied\n%s' % usage
    sys.exit(-1)

if not args and not input:
    print 'Neither command line nor file arguments supplied\n%s' % usage
    sys.exit(-1)

# Create bulk SNMP manager object
client = bulkrole.manager()

# Pass it a few options
client.timeout = timeout
client.retries = retries

# Reset global source of request IDs
serial = 0

# Build SNMP request and submit it to bulk transport from command line args
if args:
    try:
        req = eval('v'+version).GETREQUEST(request_id=serial,\
                                           community=args[1],\
                                           encoded_oids=\
                                           map(asn1.OBJECTID().encode,\
                                               args[2:]))
    except (NameError, AttributeError):
        print 'Unsupported SNMP protocol version: %s\n%s' % (version, usage)
        sys.exit(-1)

        serial = serial + 1
        
    client.append(((args[0], port), req))
    
# Read additional args from file
if input:
    # Can also read from stdin
    if input == 'stdin':
        f = sys.stdin
    else:
        try:
            f = open(input)

        except IOError, why:
            print 'open() failed: %s\n%s' % (why, usage)
            sys.exit(-1)

    while 1:
        line = f.readline()

        if not line:
            break

        args = string.split(line)

        if len(args) < 3:
            print 'Insufficient number of arguments at line: \'%s\'\n%s'\
                  % (line, usage)
            sys.exit(-1)

        try:
            req = eval('v'+version).GETREQUEST(request_id=serial,\
                                               community=args[1],\
                                               encoded_oids=\
                                               map(asn1.OBJECTID().encode,\
                                                   args[2:]))
            
        except (NameError, AttributeError):
            print 'Unsupported SNMP protocol version: %s\n%s' %\
                  (version, usage)
            sys.exit(-1)

        serial = serial + 1
        
        client.append(((args[0], port), req))

# Run the I/O
client.dispatch()

# Walk over the list of replies
for (src, rsp) in client:
    # Handle failed responses
    print 'Response from: ' + str(src)
    if rsp is None:
        print 'Timed out...'
        continue

    # Decode BER encoded Object IDs.
    oids = map(lambda x: x[0], map(asn1.OBJECTID().decode, \
                                   rsp['encoded_oids']))

    # Decode BER encoded values associated with Object IDs.
    vals = map(lambda x: x[0](), map(asn1.decode, rsp['encoded_vals']))

    # Check for remote SNMP agent failure
    if rsp['error_status']:
        print 'SNMP error #' + str(rsp['error_status']) + ' for OID #' \
              + str(rsp['error_index'])
        continue
        
    # Print out results
    for (oid, val) in map(None, oids, vals):
        print oid + ' ---> ' + str(val)
