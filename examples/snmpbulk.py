#!/usr/local/bin/python -O
#
# Retrieve certain OID/value pairs from SNMP agent. Employ parallel
# algorithm of bulk retrieval. The number of simultaneous SNMP sessions
# is limited by the maximum nuber of file descriptors available
# to process.
#
# Written by Ilya Etingof <ilya@glas.net>, 1999
#

# import basic modules
import string
import sys

# import SNMP module
import pysnmp

# OID's to look up
OBJIDS = [ '.1.3.6.1.4.1.307.3.2.1.1.1.4.1' ,
    '.1.3.6.1.4.1.307.3.2.1.1.1.4.2', 
    '.1.3.6.1.4.1.307.3.2.1.1.1.4.3', 
    '.1.3.6.1.4.1.307.3.2.1.1.1.4.4', 
    '.1.3.6.1.4.1.307.3.2.1.1.1.4.5' 
]

# send multiple GET requests at the same time for bulk
# data retrieval.
def snmpbulk (agent, community, objids):
    # initialize objid & vals lists
    encoded_oids = [ None ]
    encoded_vals = [ None ]  

    # create a multisession SNMP object
    msession = pysnmp.multisession()

    # encode objids
    for objid in objids:
        # encode an objid
        encoded_oids[0] = msession.encode_oid(msession.str2nums(objid))

        # submit encoded objid to the agent
        msession.submit_request(agent, community, 'GETREQUEST', encoded_oids, encoded_vals)

    # send submitted SNMP requests and collect replies
    msession.dispatch()

    # retrieve encoded pairs
    encoded_pairs = msession.retrieve()

    # initialize index
    response = 0

    # decode responses
    for objid in objids:
        # skip it no response
        if not encoded_pairs[response]:
            print 'no response for Object-ID %s from agent %s' % (objid, agent)
            response = response + 1
            continue

        # parse a response packet
        (encoded_oids, encoded_vals) = encoded_pairs[response]

        # decode objs & vals
        index = 0
        while index < len(encoded_oids):
            # print it out
            print msession.decode_value(encoded_oids[index]),
            print ' --> ',
            print msession.decode_value(encoded_vals[index])

            # go to the next objid
            index = index + 1

        # process next response
        response = response + 1

if __name__ == '__main__':
    # check args
    if len(sys.argv) < 3:
        print 'Usage: %s <snmp-agent> <communuty> [object-id ... ]' % sys.argv[0]
        sys.exit(1)

    # build a list of objid's
    if len(sys.argv) > 3:
        objids = sys.argv[3:]
    else:
        objids = OBJIDS

    # call the snmpbulk with args
    snmpbulk(sys.argv[1], sys.argv[2], objids)
