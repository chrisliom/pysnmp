#!/usr/local/bin/python -O
#
# An asynchronous implementation of SNMP manager.
# 
# Written by Ilya Etingof <ilya@glas.net>, 2000
#

import socket
import string
import asyncore
import asynchat
import asynsnmp

# proxy server chat class -- listens on a stream server socket, collects
# requests for SNMP lookups, creates asyncsnmp.async_session() object
class proxy_chat (asynchat.async_chat):
    """handles new proxy (stream) connection"""
    def __init__ (self, sock):
        # call constructor of the parent class
        asynchat.async_chat.__init__ (self, sock)

        # register end-of-line token
        self.set_terminator ('\r\n')

        # initialize input data buffer
        self.data = ''

        # chat constants
        self.prompt = 'query> '
        self.welcome = 'Example proxy SNMP server session opened.\n'
        self.help = 'Syntax: <SNMP agent> <SNMP community> <SNMP Object-ID>\n'

        # send welcome message
        self.send(self.welcome + self.help + self.prompt)
                  
    # put data read from socket to a buffer
    def collect_incoming_data (self, data):
        # collect data in input buffer
        self.data = self.data + data

    # callback method invoked by SNMP manager object as request completes.
    def request_done_fun (self, data, encoded_oids, encoded_vals):
        # initialize
        index = 0

        # scan through received objid's
        while index < len(encoded_oids):
            # decode objid & value, build a reply
            response = self.manager.session.decode_value(encoded_oids[index])
            response = response + ' --> '
            response = response + \
                       self.manager.session.decode_value(encoded_vals[index])
            response = response + '\n'

            # send response
            self.send(response + self.prompt)
            
            # increment index
            index = index + 1
            
    # called wnen command terminator found    
    def found_terminator (self):
        # get the command
        line = self.data
        self.data = ''

        # process the request
        response = self.parse_request(line)

        # send possible response
        if response != None:
            self.send(response + self.prompt)

    # parse up request    
    def parse_request (self, line):
        # make sure request is not empty
        if not line:
            return ''

        # split request up to fields
        args = string.split(line)

        # check args
        if len(args) < 3:
            return 'Insufficient number of arguments.\n'

        # create new SNMP manager object
        self.manager = asynsnmp.async_session(args[0], args[1], \
                                              self.request_done_fun, self)

        # initialize lists for SNMP query oids and values
        encoded_oids = []
        encoded_vals = []
        
        # encode oid
        encoded_oids.append(self.manager.session.encode_oid(\
            self.manager.session.str2nums(args[2])))
        
        # send a request
        self.manager.send_request('GETREQUEST', encoded_oids, encoded_vals)
        
        # expect reply later
        return None
    
# proxy server class -- listens for incoming requests
class proxy_server (asyncore.dispatcher):
    def __init__ (self, port=8989):
        # call parent class constructor
        asyncore.dispatcher.__init__ (self)
        
        # create socket of requested type
        self.create_socket (socket.AF_INET, socket.SOCK_STREAM)

        # set it to re-use address
        self.set_reuse_addr()
        
        # bind to specified port
        self.bind (('', port))
        
        # call listen()
        self.listen (5)

    # accept new connection (for STREAM sockets)
    def handle_accept (self):
        # accept new connection
        sock, addr = self.accept()

        # create new whoson chat object to listen to this socket
        proxy_chat(sock)

if __name__ == '__main__':
    # sys module needed for this explanation call
    import sys

    # check args
    if len(sys.argv) > 1:
        print 'Usage: ' + sys.argv[0]
        sys.exit(-1)
    
    # create proxy server object
    server = proxy_server()

    # run the select() I/O multiplexing loop
    asyncore.loop()
