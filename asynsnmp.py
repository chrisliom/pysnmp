#
# Asynchronous SNMP manager class based on Sam Rushing's asyncore classes.
# 
# Written by Ilya Etingof <ilya@glas.net>, 2000
#

import socket
import string
import asyncore
import pysnmp

# module specific exceptions
bad_parameters='Bad initialization parameters'

# send SNMP request and receive a response asynchronously
class async_session (asyncore.dispatcher):
    """An asynchronous snmp manager"""
    def __init__ (self, agent=None, community='public', \
                  caller_fun=None, caller_data=None, \
                  version=0, timeout=1.0, retries=3, port=161):
        """asynchronous SNMP manager constructor"""
        # make sure we get all these arguments
        if not caller_fun:
            raise bad_parameters

        # call parent class constructor
        asyncore.dispatcher.__init__ (self)

        # keep references to data and method objects supplied
        # by caller for callback on request completion.
        self.caller_data = caller_data
        self.caller_fun = caller_fun

        # create snmp session object
        self.session = pysnmp.session(agent, community)

        # pass snmp socket to asyncore dispatcher
        self.set_socket(self.session.open())

    # build and send SNMP request for specified Object-Id & values
    def send_request (self, type, encoded_oids, encoded_vals):
        """build send SNMP request for specified Object-Id & values"""

        # build SNMP GETREQUEST packet
        self.request = self.session.encode_request (type, \
                                                encoded_oids, \
                                                encoded_vals)

        # send request out
        self.session.send(self.request)

    # read SNMP reply from socket. this does NOT time out so one needs to
    # implement a mean of handling timed out requests (perhaps it's worth
    # looking at medusa/event_loop.py for an interesting approach).
    def handle_read (self):
        """read SNMP reply from socket"""
        # assuming the UDP layer guarantee we always get the whole message
        self.response, self.addr = self.recvfrom (8192)

        # try to decode response
        try:
            # there seems to be no point in delivering pysnmp exceptions
            # from here as they would arrive out of context...
            (encoded_oids, encoded_vals) = \
                           self.session.decode_response (self.response)

	# catch all known pysnmp exceptions and return a tuple of None's
        # as exceptions would then arrive out of context at this point.
        except tuple (pysnmp.ERROR_EXCEPTIONS) +\
               tuple ([pysnmp.bad_version, pysnmp.bad_community,\
                       pysnmp.bad_request_id, pysnmp.empty_response]):
            # return a tuple of None's to indicate the failure
            (encoded_oids, encoded_vals) = (None, None)

        # pass SNMP response back to caller
        self.caller_fun (self.caller_data, encoded_oids, encoded_vals)

    # objects of this class never expect write events
    def writable (self):
        return 0

    # objects of this class never expect connect events
    def handle_connect (self):
        pass
