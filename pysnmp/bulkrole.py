"""
   SNMP transport class.

   Sends & receives SNMP messages to multiple destinations in bulk.

   Written by Ilya Etingof <ilya@glas.net>, 1999-2002.

"""
import socket
import select

# Import PySNMP components
import role, error
import v1, v2c

class manager:
    """Send SNMP messages to multiple destinations and receive
       replies.
    """
    def __init__(self):
        # Set defaults to public attributes
        self.retries = 3
        self.timeout = 1
        self.iface = None

        self.clear()

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
        
        # [Re-]create SNMP manager transport
        self.transport = role.manager()
        self.transport.iface = self.iface

    def append(self, (dst, req)):
        """
           append((dst, req))

           Create SNMP session destined to "agent" (a tuple of (host, port)
           where host is a string and port is an integer) and queue SNMP
           "request" message (string) to be sent to "agent".

           All queued request messages will be sent upon self.dispatch() method
           invocation.
        """
        if self._durty:
            raise ValueError('List is not valid for update (try clear())')

        self._requests.append((dst, req))

    def __setitem__(self, idx, (dst, req)):
        """
        """
        if self._durty:
            raise ValueError('List is not valid for update (try clear())')
        
        try:
            self._requests[idx] = (dst, req)

        except IndexError:
            raise error.BadArgument('Request index out of range')

    def __getitem__(self, idx):
        """
        """
        try:
            return self._requests[idx]

        except IndexError:
            raise error.BadArgument('Request index out of range')

    def count(self):
        """XXX
        """
        return self._requests.count()

    def index(self, (dst, req)):
        """
        """
        if self._durty:
            raise ValueError('List is not valid for update (try clear())')

        try:
            return self._requests.index((dst, req))

        except ValueError:
            raise error.BadArgument('No such request in queue')

    def insert(self, idx, (dst, req)):
        """
        """
        if self._durty:
            raise ValueError('List is not valid for update (try clear())')

        try:
            return self._requests.insert(idx, (dst, req))

        except IndexError:
            raise error.BadArgument('Request index out of range')

    def remove(self, (dst, req)):
        """
        """
        try:
            return self._requests.remove((dst, req))

        except ValueError:
            raise error.BadArgument('No such request in queue')

    def pop(self, idx=-1):
        """
        """
        try:
            return self._requests.pop(idx)

        except IndexError:
            raise error.BadArgument('Request index out of range')

    #
    # The main I/O method
    #
    def dispatch(self):
        """
           dispatch()
           
           Send pending SNMP requests and receive replies (or timeout).
        """
        # Indicate that internal queue might change
        self._durty = 1
        
        # Initialize a list of responses
        self._responses = [ None ] * self._requests.count()

        # Initialize retry counter
        retries = self.retries
        
        while retries:
            # Send out requests and prepare for waiting for replies
            for idx in range(self._requests.count()):
                # Skip completed session
                if self._responses[idx] is None:
                    continue

                (agent, req) = self._requests[idx]

                try:
                    # While response is not received, keep [re-]sending SNMP
                    # request message
                    self.transport.send(req.encode())
                    
                except error.SNMPEngineError:
                    pass

            # Collect responses from agents
            while filter(None, self._responses):
                # Wait for response
                (response, src) = self.transport.receive()

                # Stop on timeout
                if response is None:
                    break

                # Decode response
                (rsp, rest) = v2c.decode(response)

                # Try to match response message against pending
                # request messages
                for idx in range(self._requests.count()):
                    if (src, rsp) == self._requests[idx]:
                        self._responses[idx] = (src, rsp)
                        break

        # Replace list of requests with list of replies
        self._requests = self._responses            
