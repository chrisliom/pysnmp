"""
   Sends & receives SNMP messages to multiple destinations in bulk.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
import socket
from select import select
from pysnmp.mapping.udp import role, error

class manager:
    """Send SNMP messages to multiple destinations and receive
       replies.
    """
    def __init__(self, iface=('0.0.0.0', 0)):
        # Initialize defaults
        self.iface = iface
        self.clear()

        # Set defaults to public attributes
        self.retries = 3
        self.timeout = 1

    #
    # Implement list interface
    #

    def __str__(self):
        """
        """
        return str(self._requests)

    def __repr__(self):
        """
        """
        return repr(self._requests)

    def clear(self):
        """Clear the list of sessions and prepare for next round
           of append->dispatch->subscript cycle.
        """
        self._requests = []
        self._responses = []
        self._durty = 0
        
    def append(self, (dst, question, context)):
        """
           append((dst, question, context))

           Create transport session destined to "agent" (a tuple of
           (host, port) where host is a string and port is an integer)
           and queue SNMP "question" message (string) to be sent to "dst".

           All queued request messages will be sent upon self.dispatch()
           method invocation.
        """
        if self._durty:
            raise ValueError('List is not valid for update (try clear())')

        self._requests.append((dst, question, context))

    def __setitem__(self, idx, (dst, question, context)):
        """
        """
        if self._durty:
            raise ValueError('List is not valid for update (try clear())')

        try:
            self._requests[idx] = (dst, question, context)

        except IndexError:
            raise IndexError('Request index out of range')

    def __getitem__(self, idx):
        """
        """
        try:
            return self._requests[idx]

        except IndexError:
            raise IndexError('Request index out of range')

    def __len__(self):
        """
        """
        return len(self._requests)
                   
    def count(self, val):
        """XXX
        """
        return self._requests.count(val)

    def index(self, (dst, question, context)):
        """
        """
        if self._durty:
            raise ValueError('List is not valid for update (try clear())')

        try:
            return self._requests.index((dst, question, context))

        except ValueError:
            raise ValueError('No such request in queue')

    def insert(self, idx, (dst, question, context)):
        """
        """
        if self._durty:
            raise ValueError('List is not valid for update (try clear())')

        try:
            return self._requests.insert(idx, (dst, question, context))

        except IndexError:
            raise IndexError('Request index out of range')

    def remove(self, (dst, question, context)):
        """
        """
        try:
            return self._requests.remove((dst, question, context))

        except ValueError:
            raise ValueError('No such request in queue')

    def pop(self, idx=-1):
        """
        """
        try:
            return self._requests.pop(idx)

        except IndexError:
            raise IndexError('Request index out of range')

    #
    # The main I/O method
    #
    def dispatch(self):
        """
           dispatch()
           
           Send pending SNMP requests and receive replies (or timeout).
        """
        # Indicate that internal queue has changed
        self._durty = 1

        # Resolve destination hostnames to IP numbers for later comparation
        try:
            self._requests = map(lambda (dst, question, context): \
                                 ((socket.gethostbyname(dst[0]), \
                                   dst[1]), question, context),\
                                 self._requests)

        except socket.error, why:
            raise error.BadArgumentError(why)

        # Initialize a list of responses
        self._responses = map(lambda (dst, req, context): \
                              (dst, None, context), self._requests)

        # Initialize a list of transports
        transports = [ None ] * len(self._requests)
        
        # Initialize retry counter
        retries = self.retries

        while retries and len(filter(lambda x: x == None, \
                                 map(lambda x: x[1], self._responses))):
            # Send out requests and prepare for waiting for replies
            for idx in range(len(self._responses)):
                # Skip completed session
                (src, answer, context) = self._responses[idx]
                if answer is not None:
                    continue

                (dst, question, context) = self._requests[idx]

                # Create SNMP manager transport if needed
                if transports[idx] is None:
                    transports[idx] = role.manager((None, 0), self.iface)

                # Send request to agent
                try:
                    transports[idx].send(question, dst)
                    
                except error.SnmpOverUdpError, why:
                    # Return exception
                    self._responses[idx] = (self._responses[idx][0], why,\
                                            self._responses[idx][2])

            # Collect responses from agents
            while len(filter(lambda x: x == None, map(lambda x: x[1], \
                                                      self._responses))):
                # Initialize a list of sockets to listen on
                r = []
                for idx in range(len(self._responses)):
                    # Skip completed session
                    (src, answer, context) = self._responses[idx]
                    if answer is None and transports[idx] is not None:
                        r.append(transports[idx].get_socket())

                (r, w, x) = select(r, [], [], self.timeout)

                # On timeout
                if len(r) == 0:
                    retries = retries - 1
                    break

                for s in r:
                    for idx in range(len(transports)):
                        if transports[idx] is not None and \
                           transports[idx].get_socket() == s:
                            try:
                                (answer, src) = transports[idx].receive()

                            except error.SnmpOverUdpError, why:
                                # Return exception
                                self._responses[idx] = (self._responses[idx][0],\
                                                        why,\
                                                        self._responses[idx][2])
                            else:
                                self._responses[idx] = (src, answer, \
                                                        self._responses[idx][2])
                            break

        # Replace list of requests with list of replies
        self._requests = self._responses            
