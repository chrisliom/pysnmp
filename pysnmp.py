#
# SNMP manager class
#
# Written by Ilya Etingof <ilya@glas.net>, 1999
#

# import system modules
import string
import socket
import select
import whrandom

# import BER module
import ber

# module specific exceptions
bad_parameters='Bad initialization parameters'
bad_argument='Bad argument'
not_connected='Not connected'
no_response='No response arrived before timeout'
bad_version='Unsupported protocol version in response'
bad_community='Bad community in response'
bad_request_id='Request ID mismatched'
empty_response='Empty response'
illegal_argument='Illegal argument'

# SNMP error exceptions (taken from UCD SNMP code)
ERROR_EXCEPTIONS = [
    '(noError) No Error',
    '(tooBig) Response message would have been too large.',
    '(noSuchName) There is no such variable name in this MIB.',
    '(badValue) The value given has the wrong type or length.',
    '(readOnly) The two parties used do not have access to use the specified SNMP PDU.',
    '(genError) A general failure occured.',
    # the rest is unlikely to ever be reported by a v.1 agent
    '(noAccess) Access denied.',
    '(wrongType) Wrong BER type',
    '(wrongLength) Wrong BER length.',
    '(wrongEncoding) Wrong BER encoding.',
    '(wrongValue) Wrong value.',
    '(noCreation) ',
    '(inconsistentValue) ',
    '(resourceUnavailable) ',
    '(commitFailed) ',
    '(undoFailed) ',
    '(authorizationError) ',
    '(notWritable) ',
    '(inconsistentName) '
]

# encode / decode SNMP packet
class packet (ber.ber):
    # initialize version and community
    def __init__ (self, version=0, community='public'):
        # make sure we get all these arguments
        if version == None or not community:
            raise bad_parameters

        # initialize SNMP specific variables
        self.request_id = long (whrandom.random()*0x7fffffff)
        self.version = version
        self.community = community

    #
    # ENCODERS
    #

    # encode oid's & values pairs
    def encode_bindings (self, encoded_oids, encoded_values):
        """bind together encoded object ID's and their optional values"""
        # get the number of oids to encode
        size = len(encoded_oids)

        # make sure the list is not empty
        if not size:
            raise bad_argument

        # initialize stuff
        index = 0
        encoded_oid_pairs = ''

        # encode encoded objid's and encoded values together
        while index < size:
            # encode and concatnate one oid_pair
            if encoded_values and encoded_values[index]:
                # merge oid with value
                oid_pairs = encoded_oids[index] + \
                            encoded_values[index]
            else:
                # merge oid with value
                oid_pairs = encoded_oids[index] + \
                            self.encode_null()

            # encode merged pairs
            encoded_oid_pairs = encoded_oid_pairs + \
                self.encode_sequence (oid_pairs)

            # progress index
            index = index + 1

        # return encoded bindings
        return self.encode_sequence(encoded_oid_pairs)

    # encode pdu
    def encode_snmp_pdu (self, type, request):
        """encode variables bindings into SNMP PDU"""
        # increment the request ID counter
        self.request_id = self.request_id + 1

        # build a PDU
        result = self.encode_integer(self.request_id) + \
            self.encode_integer(0) + \
            self.encode_integer(0) + \
            request

        # encode the whole pdu
        return  self.encode_snmp_pdu_sequence(type, result)

    # wrap up SNMP PDU
    def encode_request_sequence (self, request):
        """encode SNMP PDU into SNMP request"""
        # merge version & community & request
        result = self.encode_integer (self.version) + \
            self.encode_string (self.community) + \
            request

        # encode the whole request
        return self.encode_sequence (result)

    # build SNMP request of specified type from encoded oid & value pairs
    def encode_request (self, type='GETREQUEST', encoded_oids=[], encoded_values=[]):
        """build SNMP request packet of specified type from encoded
           OID's and values"""
        # encode variables bindings
        result = self.encode_bindings (encoded_oids, encoded_values)

        # encode getreq pdu
        result = self.encode_snmp_pdu (type, result)

        # encode pdu into SNMP request
        result = self.encode_request_sequence (result)

        # return SNMP request
        return result

    #
    # DECODERS
    #

    # unwrap response, return pdu
    def decode_response_sequence (self, request):
        """parse out SNMP PDU from SNMP request"""
        # unwrap the whole packet
        packet = self.decode_sequence (request)

        # decode SNMP version
        length, size = self.decode_length (packet[1:])
        version = self.decode_integer (packet)
    
        # update packet index
        index = size + length + 1

        # decode community
        length, size = self.decode_length (packet[index+1:])
        community = self.decode_string (packet[index:])

        # update packet index
        index = index + size + length + 1

        # return SNMP version, community and the rest of packet
        return (version, community, packet[index:])

    # decode pdu
    def decode_pdu (self, packet):
        """decode SNMP PDU"""
        # get pdu tag
        tag = self.decode_tag(ord(packet[0]))

        # decode pdu
        pdu = self.decode_sequence (packet)

        # get request ID from PDU
        length, size = self.decode_length (pdu[1:])
        request_id = self.decode_unsigned (pdu)

        # update packet index
        index = size + length + 1

        # get error status field
        length, size = self.decode_length (pdu[index+1:])
        error_status = int(self.decode_integer (pdu[index:]))

        # update packet index
        index = index + size + length + 1

        # get error index field
        length, size = self.decode_length (pdu[index+1:])
        error_index = int(self.decode_integer (pdu[index:]))

        # update packet index
        index = index + size + length + 1

        # return encoded variables bindings
        return (tag, request_id, error_status, error_index, pdu[index:])

    # decode oid's & values bindings
    def decode_bindings (self, packet):
        """decode variables bindings"""
        # decode bindings
        bindings = self.decode_sequence (packet)

        # initialize objids and vals lists
        encoded_oids = []
        encoded_vals = []

        # initialize index
        index = 0

        # cycle through bindings
        while index < len(bindings):
            # get a binding
            length, size = self.decode_length (bindings[index+1:])
            binding = self.decode_sequence (bindings[index:])

            # get the binding length
            binding_length = length + size + 1

            # get the oid length
            length, size = self.decode_length (binding[1:])
            oid_length = length + size + 1

            # get an encoded oid
            encoded_oids.append(binding[:oid_length])

            # get an encoded value
            encoded_vals.append(binding[oid_length:])

            # move to the next binding
            index = index + binding_length

        # return encoded_oids & encoded_vals
        return (encoded_oids, encoded_vals)

    # decode SNMP response, check the type, return encoded
    # oid & value pairs
    def decode_response (self, packet=None, type='GETRESPONSE'):
        """decode SNMP response, return encoded OID's and values"""
        # make sure the response packet is specified
        if not packet:
            raise empty_response

        # unwrap the whole packet
        (version, community, response) = self.decode_response_sequence(packet)

        # check response validness
        if version != self.version:
            raise bad_version
        if community != self.community:
            raise bad_community

        # decode pdu
        (tag, request_id, error_status, error_index, response) = \
                         self.decode_pdu (response)

        # make sure request ID's matched
        if request_id != self.request_id:
            raise bad_request_id, (request_id, self.request_id)

        # check the PDU type if given
        if type and tag == self.encode_tag(type):
            raise bad_pdu_type

        # check error status
        if error_status > 0:
            # an error occurred
            raise ERROR_EXCEPTIONS[error_status], error_index

        # decode variables bindings
        (encoded_oids, encoded_values) = self.decode_bindings(response)

        # return encoded OID's and values
        return (encoded_oids, encoded_values)


# send SNMP request and receive a response
class session (packet):
    # init the session
    def __init__ (self, agent=None, community='public', version=0, \
            timeout=1.0, retries=3, port=161):
        # call packet class constructor
        packet.__init__ (self, version, community)

        # make sure we get all these arguments
        if not agent or not port or \
                timeout == None or retries == None:
            raise bad_parameters

        # initialize SNMP session
        self.agent = agent
        self.port = port
        self.timeout = timeout
        self.retries = retries

        # this is a provision for multisession superclass
        self.request = None
        self.response = None

        # initialize socket
        self.socket = None

    # store packet for later transmission
    def store (self, request=None):
        """store SNMP packet for later transmission"""
        if not request:
            raise bad_argument
        self.request = request

    # return socket object
    def get_socket (self):
        """return socket object previously created with open() method"""
        return self.socket

    # open a socket for SNMP agent
    def open (self):
        """create a UDP socket to SNMP agent"""
        # create a socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((self.agent, self.port))

        # return socket object
        return self.socket

    # send a packet down to agent
    def send (self, request=None):
        """send SNMP packet to agent"""
        # packet must present
        if not request and not self.request:
            raise bad_argument

        # store new request
        if request:
            self.store (request)

        # make sure the connection is established, open it otherwise
        if not self.socket:
            self.open()

        # send out a packet
        self.socket.send(self.request)

    # read data up from the socket (presuming it is ready for readung)
    def read (self):
        # make sure the connection exists
        if not self.socket:
            raise not_connected

        # read up data from the socket
        self.response = self.socket.recv(1024)

        # return response
        return self.response
        
    # receive a response with timeout
    def receive (self):
        """receive a response from SNMP agent"""
        # initialize sockets map
        r, w, x = [self.socket], [], []

        # wait for response
        r, w, x = select.select(r, w, x, self.timeout)

        # timeout occured?
        if r:
            # read up data from the socket
            self.response = self.socket.recv(1024)

            # return response
            return self.response

        # return nothing on timeout
        return None

    # send request and receive a reply
    def send_and_receive (self, packet):
        """send SNMP request and receive a reply with timeout"""
        # initialize retries counter
        retries = 0

        # send request till response or retry counter hits the limit
        while retries < self.retries:
            # send a request
            self.send (packet)

            # wait for response
            response = self.receive ()

            # succeeded?
            if response:
                return response

            # otherwise, try it again
            retries = retries + 1

        # no answer
        raise no_response

    # close the socket
    def close (self):
        """close UDP socket to SNMP agent"""
        # close socket
        if self.socket:
            self.socket.close()
            self.socket = None  

# perform multiple SNMP queries virtually simultaneously
class multisession (session):
    # init the session
    def __init__ (self, timeout=1.0, retries=3, version=0):
        # initialize common settings for all the SNMP sessions
        self.timeout = timeout
        self.retries = retries
        self.version = version

        # create a list of active sessions
        self.sessions = []

        # create a list of encoded pairs
        self.encoded_pairs = []

    # submit new SNMP request
    def submit_request (self, agent=None, community='public', \
            type='GETREQUEST', \
            encoded_oids=None, encoded_vals=None,\
            port=161):
        """create new SNMP Get-Request and add it to a list of sessions"""
        # create new SNMP session
        ses = session (agent, community, port=port)

        # build a SNMP packet
        packet = ses.encode_request(type, encoded_oids, encoded_vals)

        # store the packet to be sent in the session object
        ses.store (packet)

        # try to create a socket (used for indexing).
        # trap is suggested by Case Van Horsen to handle send() failure, 05/2000
        try:
            ses.open()
        except socket.error:
            ses = None

        # add it to the list of active sessions
        self.sessions.append(ses)

    # receive responses
    def dispatch (self):
        """send SNMP requests and receive replies with timeout"""
        # initialize retries counter
        retries = 0

        # try to get responses from all the agents
        while retries < self.retries:
            # initialize sockets map
            r, w, x = [], [], []

            # send out requests and prepare for waiting for replies
            for ses in self.sessions:
                # skip refused session.
                # suggested by Case Van Horsen to handle failed sessions, 05/2000.
                if not ses:
                    continue

                # skip completed session
                if ses.response:
                    continue

                # this trap is suggested by Case Van Horsen to handle send() failure, 05/2000
                try:
                    # try send this session's packet
                    ses.send()

                    # add this session's socket into the sockets map
                    r.append(ses.socket)
                except socket.error:
                    pass

            # stop if we get responses from all agents
            if not r:
                break

            # wait for response
            r, w, x = select.select(r, w, x, self.timeout)

            # response arrived
            if r:
                # scan through the list of active sockets 
		# (socket variable replaced with sock as Case Van Horsen
		# reported that it interferes with the socket module, 05/2000)
                for sock in r:
                    # find corresponding socket
                    for ses in self.sessions:
                        # skip failed sessions.
                        # suggested by Case Van Horsen to handle failed sessions, 05/2000.
                        if not ses:
                            continue

                        # see if response arrived for this session
                        if ses.socket == sock:
                            # this trap is suggested by Case Van Horsen to handle
                            # read() * close() failures, 05/2000
                            try:
                                # read up data from the socket
                                ses.read ()

                                # close this session
                                ses.close ()

                            except socket.error:
                                pass
                            
                            # process only one socket
                            break
            else:
                # timeout occurred
                retries = retries + 1

        # close all the sockets
        for ses in self.sessions:
            # skip failed sessions.
            # suggested by Case Van Horsen to handle failed sessions, 05/2000.
            if not ses:
                continue

            # close this socket
            if ses.socket:
                ses.close ()

    # retrieve replies (some may be None)
    def retrieve (self):
        """retrieve received SNMP replies"""
        # build the list of responses
        for ses in self.sessions:
            # skip failed sessions.
            # suggested by Case Van Horsen to handle failed sessions, 05/2000.
            if not ses:
                encoded_pairs = None
            # decode response for this session if present
            elif not ses.response:
                encoded_pairs = None
            else:
                encoded_pairs = ses.decode_response(ses.response)

            # append response to the list of responses
            self.encoded_pairs.append(encoded_pairs)
    
        # return the list of responses (some may be None)
        return self.encoded_pairs
