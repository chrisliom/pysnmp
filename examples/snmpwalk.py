#!/usr/local/bin/python -O
#
# Look up lexicographically next larger OID/value pairs at SNMP agent
#
# Written by Ilya Etingof <ilya@glas.net>, 1999
#

# import basic modules
import string
import sys

# import SNMP module
import pysnmp

# OID's to lookup
OBJIDS = [ '.1.3.6.1.4.1.307.3.2.1.1.1.4.0' ]

# query a SNMP agent for OID's
def snmpwalk (agent, community, objids):
    # initialize objid & vals lists
    encoded_oids = []
    encoded_vals = []

    # create a SNMP session
    session = pysnmp.session(agent, community)

    # encode objids
    for objid in objids:
        # encode an objid
        encoded_oids.append(session.encode_oid(session.str2nums(objid)))

    # traverse the agent's MIB
    while 1:
        # build a packet
        packet = session.encode_request ('GETNEXTREQUEST', encoded_oids, encoded_vals)

        # send SNMP request and recieve a response
        packet = session.send_and_receive (packet)

        # parse a response packet
        (encoded_oids, encoded_vals) = session.decode_response (packet)

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
    if len(sys.argv) < 3:
        print 'Usage: %s <snmp-agent> <communuty> [object-id ... ]' % sys.argv[0]
        sys.exit(1)

    # build a list of objid's
    if len(sys.argv) > 3:
        objids = sys.argv[3:]
    else:
        objids = OBJIDS

    # call the snmpwalk with args
    snmpwalk(sys.argv[1], sys.argv[2], objids)
