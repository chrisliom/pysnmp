#!/usr/local/bin/python -O
"""
   Retrieve a SNMP table of Object IDs starting from user specifed SNMP
   Object ID(s) from arbitrary SNMP agent using SNMP v.2 GETBULK PDU.

   Since MIB parser is not yet implemented in Python, this script takes and
   reports Object IDs in dotted numeric representation only.

   Written by Ilya Etingof <ilya@glas.net>, 2000-2002

"""
import sys
import getopt

# Import PySNMP modules
from pysnmp import asn1, v2c
from pysnmp import role

# Initialize help messages
options =           'Options:\n'
options = options + '  -p <port>      port to communicate with at the agent. Default is 161.\n'
options = options + '  -r <retries>   number of retries to be used in requests. Default is 5.\n'
options = options + '  -t <timeout>   timeout between retries. Default is 1.\n'
usage = 'Usage: %s [options] <snmp-agent> <community> <obj-id [[obj-id] ... ]\n' % sys.argv[0]
usage = usage + options
    
# Initialize defaults
port = 161
retries = 5
timeout = 1

# Parse possible options
try:
    (opts, args) = getopt.getopt(sys.argv[1:], 'hp:r:t:',\
                                 ['help', 'port=', 'retries=',\
                                  'timeout='])
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

except ValueError, why:
    print 'Bad parameter \'%s\' for option %s: %s\n%s' \
          % (opt[1], opt[0], why, usage)
    sys.exit(-1)

if len(args) < 3:
    print 'Insufficient number of arguments supplied\n%s' % usage
    sys.exit(-1)

# Create SNMP manager object
client = role.manager((args[0], port))

# Pass it a few options
client.timeout = timeout
client.retries = retries

# Create a SNMP request&response objects
req = v2c.GETBULKREQUEST(community=args[1], \
                         non_repeaters=0, max_repetitions=256)
rsp = v2c.RESPONSE()

# Store table headers
head_oid = asn1.OBJECTID(args[2])

# BER encode initial SNMP Object IDs to query
encoded_oids = [ head_oid.encode() ]

# Traverse agent MIB
while 1:
    # Encode SNMP request message and try to send it to SNMP agent
    # and receive a response
    (answer, src) = client.send_and_receive(\
                    req.encode(encoded_oids=encoded_oids))

    # Attempt to decode SNMP response
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
        # SNMP agent reports 'no such name' when walk is over XXX
        if rsp['error_status'] == 2:
            # One of the tables exceeded
            for l in oids, vals, head_oids:
                del l[rsp['error_index']-1]
        else:
            raise 'SNMP error #' + str(rsp['error_status']) + ' for OID #' \
                  + str(rsp['error_index'])

    # Cut OID list by fisrt non-prefix OID
    for idx in range(len(oids)):
        if not head_oid.isaprefix(oids[idx]):
            oids = oids[:idx]
            vals = vals[:idx]
            break
        
    if not oids:
        sys.exit(0)
        
    # Print out results
    for (oid, val) in map(None, oids, vals):
        print oid + ' ---> ' + str(val)

    # BER encode next SNMP Object IDs to query
    encoded_oids = map(asn1.OBJECTID().encode, oids[-1:])

    # Update request object
    req['request_id'] = req['request_id'] + 1
