#!/usr/local/bin/python
import pysnmp
import types
import UserDict
import bisect
import objid
import SocketServer
import re

############################################################################
#
# snmpagent .1 
#
# A limited snmpv1 agent hacked off the pysnmp library.
#
# Cayce Ullman (cayce@actzero.com)
#
############################################################################

# For determining if something is an ip address.
ipaddr_re = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

############################################################################
#
# OidDict
#
# This is keeps oids in your typically dictionary
# except that it keeps a sorted list for the implementation
# of GETNEXTREQUEST.  This is implemented very poorly in
# in terms of performance if one is adding to the oid dict often.
# probably should be re-implemented so that it will handle more oids,
# faster.
#
############################################################################
class OidDict(UserDict.UserDict, objid.objid):
    ########################################################################
    #
    # __init__
    #
    ########################################################################
    def __init__(self, dict=None):
        UserDict.UserDict.__init__(self, dict)
        self._resort()

    ########################################################################
    #
    # _resort
    #
    # Break down the oids into numbers and sort.
    #
    ########################################################################
    def _resort(self):
        self.sorted = self.data.keys()
        # Convert the list to a list of ints,
        # obviously this could be much faster

        i = 0
        while i < len(self.sorted):
            # convert string into a list of nums
            self.sorted[i] = self.str2nums(self.sorted[i])
            i = i + 1

        self.sorted.sort()        

    ########################################################################
    #
    # __setitem__
    #
    # Sets an item, retriggers a sort
    #
    #
    ########################################################################
    def __setitem__(self, key, item):
        UserDict.UserDict.__setitem__(self, key, item)
        self._resort()

    ########################################################################
    #
    # update
    #
    # Update a dict, retriggers a sort
    #
    ########################################################################
    def update(self, dict):
        UserDict.UserDict.update(self, dict)
        self._resort()

    ########################################################################
    #
    # clear
    #
    # Clears a dict, empties out the sorted list
    #
    ########################################################################
    def clear(self):
        UserDict.UserDict.clear(self)
        self.sorted = []

    ########################################################################
    #
    # getNextKey
    #
    # Returns the nexts oid, for GETNEXTREQUEST
    #
    ########################################################################
    def getNextKey(self, item):
        try:
            retval = self.nums2str(\
            self.sorted[bisect.bisect(self.sorted, \
                                      self.str2nums(item))])

            return retval
        except:
            return item
            

############################################################################
#
# snmpagent
#
# This is a hacked subclass of the pysnmp.packet class.  Basically
# it tries to allow one to use the pysnmp module for snmpagent creation.
#
# Now supports
#
# GETREQUEST
# GETNEXTREQUEST
# SETREQUEST    
#
# Right now items in the oid dict do not contain type.  It basically
# allows the snmpagent to determine the type.  This might need typing at
# some point.
#
############################################################################
class snmpagent(pysnmp.packet):
    ########################################################################
    #
    # __init__
    #
    # construct the snmpagent and wipe out the randomly generated
    # request_id
    #
    ########################################################################
    def __init__ (self, community='public', version=0):
        # call packet class constructor
        pysnmp.packet.__init__ (self, version, community)
        
        # Lets empty out the request_id to avoid confusion
        self.request_id = 0L
        self.error = 0
        self.error_index = 0

    ########################################################################
    #
    # decode_request_sequence
    #
    # Rename the decode_response_sequence method to hide
    # some inconsistancy
    #
    ########################################################################
    def decode_request_sequence(self, packet):
        # Hide the fact that this is labeled with request
        return self.decode_response_sequence(packet)

    ########################################################################
    #
    # decode_request
    #
    # Decodes a request, right just returns the tag, oids and values
    #
    ########################################################################
    def decode_request(self, packet):
        (version, community, packet) = self.decode_request_sequence(packet)

        # Should check community and version here
        if version != self.version:
            raise "Bad version"
        if community != self.community:
            raise "Bad community"
        
        (tag, req_id, e_status, e_index, packet) =  self.decode_pdu(packet)

        self.request_id = req_id  # Set the internal request_id for response

        (oids, vals) = self.decode_bindings(packet)

        return (tag, oids, vals)

    ########################################################################
    #
    # decode_list
    #
    # decodes a list of values or oids.
    #
    ########################################################################
    def decode_list(self, list):
        olist = []

        for i in list:
            olist.append(self.decode_value(i))

        return olist

    ########################################################################
    #
    # encode_snmp_pdu
    #
    # Overridden to stop the increment of the request_id, and
    # to allow the setting of errors.
    ########################################################################
    def encode_snmp_pdu (self, type, request):
        # build a PDU
        result = self.encode_integer(self.request_id) + \
            self.encode_integer(self.error) + \
            self.encode_integer(self.error_index) + \
            request

        # encode the whole pdu
        return self.encode_snmp_pdu_sequence(type, result)

    ########################################################################
    #
    # encode_response
    #
    # A wrapper around encode_request, plus it syncs up the request
    # ids.
    #
    ########################################################################
    def encode_response(self, type="GETRESPONSE", oids=[], vals=[]):
        return self.encode_request(type, oids, vals)

    ########################################################################
    #
    # encode_vals
    #
    # Builds the vals out of a dictionary, determines type of the data
    # and encodes accordingly.  Right now only supports ints, and strings.
    # Additionally, if you point an oid in your dictionary at a function
    # it will call the function to get the data to encode.
    #
    ########################################################################
    def get_response_vals(self, dict, oidlist):

        encoded_oids = []
        encoded_vals = []

        count = 1
        for o in oidlist:
            # encode the oid
            
            encoded_oids.append(self.encode_oid(self.str2nums(o)))

            if dict.has_key(o):
                v = dict[o]

                # encode the value
                # todo add ipaddr, uptime, timeticks etc...
                ev = None
                while ev == None:
                    
                    # String or IP ADDR
                    if type(v)==types.StringType:
                        if ipaddr_re.match(v)==None:
                            ev = self.encode_string(v)
                        else:
                            ev = self.encode_ipaddr(v)

                    # Int
                    elif type(v)==types.IntType:
                        ev = self.encode_integer(v)

                    # Function
                    elif type(v)==types.FunctionType or \
                         type(v)==types.MethodType  or \
                         type(v)==types.BuiltinFunctionType or \
                         type(v)==types.BuiltinMethodType:
                        v = v()

                    # Force a flot to int, mostly for time.time
                    elif type(v)==types.FloatType:
                        ev = self.encode_integer(int(v))

                    # Don't know what it is
                    else :
                        ev = self.encode_null()

                count = count + 1
                encoded_vals.append(ev)
            else:
                self.error = 2 
                self.error_index = count
                encoded_vals.append(self.encode_null())

        return (encoded_oids, encoded_vals)

############################################################################
#
# SNMPHandler
#
# 
# 
############################################################################
class SNMPHandler(SocketServer.DatagramRequestHandler):
    def handle(self):

        # pull the variables
        
        oid_dict   = self.server.oid_dict
        enable_set = self.server.enable_set
        
        agent = snmpagent("public")


        # get the packet data
        packet = self.rfile.read()
        #packet = self.packet
        # decode it
        (type, oids, vals) = agent.decode_request(packet)

        # Decode the list
        oids = agent.decode_list(oids)

        resptype = "GETRESPONSE"
        
        # Rebuild the value list because of the next nature
        if type=="GETNEXTREQUEST":
            tlist = []
            count = 1
            for o in oids:
                no = oid_dict.getNextKey(o)
                if no==o:
                    agent.error = 2
                    agent.error_index = count
                tlist.append(no)
                count = count + 1
            oids = tlist
        elif type=="SETREQUEST":
            if not enable_set:
                agent.error = 4
                agent.error_index = 0
            else:
                index = 0
                while index < len(oids):
                    if oid_dict.has_key(oids[index]):
                        # Right now this only works with strings
                        v = vals[index]
                        if v[0]=='\004':  # string
                            v = agent.decode_string(v)
                        elif v[0] == '\002': # int
                            v = int(agent.decode_integer(v))
                        elif v[0] == '\100': # ipaddr
                            v = agent.decode_ipaddress(v)

                        oid_dict[oids[index]] = v
                    else:
                        agent.error = 2
                        agent.error_index = index + 1
                        
                    index = index + 1
                        
        
        # Now let's respond.
        ( encoded_oids, encoded_vals) = agent.get_response_vals(oid_dict, oids)
        
        # encode the response
        packet = agent.encode_response (resptype, encoded_oids, encoded_vals )

        # Now all we got to do is send it back.
        self.wfile.write(packet)


############################################################################
#
# SNMPServer
#
# An snmp serverclass that uses hold a ref to a dict with the
# values to manipulate.
#
############################################################################
class SNMPServer(SocketServer.UDPServer):
    def __init__(self, addr, handler, oid_dict, enable_set = 1):

        SocketServer.UDPServer.__init__(self, addr, handler)
        self.oid_dict = oid_dict
        self.enable_set = enable_set

############################################################################
#
# __main__
#
# An example snmp agent with some dummy data
#
############################################################################
if __name__ == "__main__":

    import time
    
    oid_dict = {".1.2.3.4.5.6.7.8.8": "monkey",
                ".1.2.3.4.5.6.7.8.9": 4,
                ".1.2.3.4.5.6.7.8.10": time.time,
                ".1.2.3.4.5.6.7.8.11": "10.1.1.1" }
                
    oid_dict = OidDict(oid_dict)


    serv = SNMPServer(("",161), SNMPHandler, oid_dict)
    serv.serve_forever()
