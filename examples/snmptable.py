#!/usr/local/bin/python -O
#
# Retrieve a table at SNMP agent
#
# Written by Ilya Etingof <ilya@glas.net>, 1999
#

# import basic modules
import string
import sys

# import SNMP module
import pysnmp

# OID's to lookup (this seems to be IP routing table at PM2)
OBJIDS = [ '.1.3.6.1.2.1.3.1.1.3.1.1' ]

# query a SNMP agent for table
def snmptable (agent, community, objids):
    # initialize objid & vals lists (pysnmp methods
    # expect lists as input args)
    encoded_oids = []
    encoded_vals = []

    # create a SNMP session
    session = pysnmp.session(agent, community)

    # encode objid
    encoded_oids.append(session.encode_oid(session.str2nums(objids[0])))

    # remember the head of the table
    head_enc_oid = encoded_oids[0]

    # traverse the agent's MIB
    while 1:
        # build a packet
        packet = session.encode_request ('GETNEXTREQUEST', encoded_oids, encoded_vals)

        # send SNMP request and recieve a response
        packet = session.send_and_receive (packet)

        # parse a response packet
        (encoded_oids, encoded_vals) = session.decode_response (packet)

        # stop at the end of the table
        if not session.oid_prefix_check(head_enc_oid, encoded_oids[0]):
            break

        # decode objids & vals
        index = 0
        while index < len(encoded_oids):
            # print it out
            print session.decode_value(encoded_oids[index]),
            print ' --> ',
            print session.decode_value(encoded_vals[index])

            # go to the next objid
            index = index + 1

if __name__ == '__main__':
    # check args
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print 'Usage: %s <snmp-agent> <communuty> [object-id ]' % sys.argv[0]
        sys.exit(1)

    # get the top objid
    if len(sys.argv) > 3:
        objids = sys.argv[3:]
    else:
        objids = OBJIDS

    # call snmptable with args
    snmptable(sys.argv[1], sys.argv[2], objids)
