#!/usr/local/bin/python -O
#
# Set a value of certain OID at SNMP agent
#
# Written by Ilya Etingof <ilya@glas.net>, 1999
#

# import basic modules
import sys

# import SNMP module
import pysnmp

# default OID-value pairs to set to value
OBJID_PAIRS = { '.1.3.6.1.4.1.307.3.2.1.1.1.4.1' : 'a value', \
        '.1.3.6.1.4.1.307.3.2.1.1.1.4.2' : 'a value' }

# attempt to set a value of given OID-value pairs at SNMP agent
def snmpset (agent, community, objid_pairs):
    # initialize objid & vals lists
    encoded_oids = []
    encoded_vals = []

    # create a SNMP session
    session = pysnmp.session(agent, community)

    # encode objid_pairs
    for key in objid_pairs.keys():
        # encode an objid
        encoded_oids.append(session.encode_oid(session.str2nums(key)))

        # encode a value (assuming it is a string)
        encoded_vals.append(session.encode_string(objid_pairs[key]))

    # build a packet
    packet = session.encode_request ('SETREQUEST', encoded_oids, encoded_vals)

    # send SNMP request and recieve a response
    packet = session.send_and_receive (packet)

    # parse a response packet
    (encoded_oids, encoded_vals) = session.decode_response (packet)

    # decode objs & vals
    index = 0
    while index < len(encoded_oids):
        # print it out
        print session.decode_value(encoded_oids[index]),
        print ' --> ',
        print session.decode_value(encoded_vals[index])

        # go to the next objid
        index = index + 1

if __name__ == '__main__':
    # creata a dictionary of objid-value pairs passed as an argument
    objid_pairs = {}
    
    # check args
    if len(sys.argv) < 3:
        print 'Usage: %s <snmp-agent> <communuty> [object-id:value ... ]' % sys.argv[0]
        sys.exit(1)

    # build a list of objid's
    if len(sys.argv) > 3:
        for arg in sys.argv[3:]:
            # split token on objid and value
            token = string.split(arg, ':')

            # add them to the dictionary
            if len(token) == 2:
                objid_pairs[token[0]] = token[1]
            else:
                print 'bad argument: ', arg
                
    else:
        objid_pairs = OBJID_PAIRS

    # call the snmpset with args
    snmpset(sys.argv[1], sys.argv[2], objid_pairs)
