"""
   SNMP v.1 engine class.

   Sends & receives SNMP v.1 messages.

   Written by Ilya Etingof <ilya@glas.net>, 1999, 2000, 2001

"""
import socket
import select
from types import TupleType

# Import package components
#import message
import error

class manager:
    """SNMP manager: send and receive SNMP messages.
    """
    def __init__(self, agent=None):
        # If agent name is given, it may be a plain string (for
        # compatibility reasons)
        if not agent:
            self.agent = None
            self.port = None
        elif type(agent) == TupleType:
            self.agent = agent[0]
            self.port = agent[1]
        else:
            self.agent = agent
            self.port = 161

        # Initialize SNMP session
        self.timeout = 1.0
        self.retries = 3
        self.iface = None

        # Initialize socket
        self.socket = None

    def __del__(self):
        """Close socket on object termination
        """
        try:
            self.close()

        except error.TransportError:
            pass
        
    def get_socket(self):
        """
           get_socket() -> socket

           Return socket object previously created with open() method.
        """
        return self.socket

    def open(self):
        """
           open()
           
           Initialize transport layer (UDP socket) to be used
           for further communication with remote SNMP process.
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        except socket.error, why:
            raise error.TransportError('socket() error: ' + str(why))

        # See if we need to bind to specific interface at SNMP
        # manager machine
        if self.iface:
            try:
                self.socket.bind((self.iface[0], 0))

            except socket.error, why:
                raise error.TransportError('bind() error: ' + str(why))

        # Connect to default destination if given
        if self.agent:
            try:
                self.socket.connect((self.agent, self.port))

            except socket.error, why:
                raise error.TransportError('connect() error: ' + str(why))

        return self.socket

    def send(self, request, dst=None):
        """
           send(request[, dst])
           
           Send SNMP "request" message to remote SNMP process specified on
           session object creation or by "dst" address given in socket
           module notation.
        """
        # Make sure the connection is established, open it otherwise
        if not self.socket:
            self.open()

        try:
            if dst:
                self.socket.sendto(request, dst)
            else:    
                self.socket.send(request)

        except socket.error, why:
            raise error.TransportError('send() error: ' + str(why))

    def read(self):
        """
           read() -> (message, src)
           
           Read data from the socket (assuming there's some data ready
           for reading), return a tuple of SNMP message (as string)
           and source address 'src' (in socket module notation).
        """   
        # Make sure the connection exists
        if not self.socket:
            raise error.NotConnected

        try:
            (message, src) = self.socket.recvfrom(65536)

        except socket.error, why:
            raise error.TransportError('recv() error: ' + str(why))

        return (message, src)
        
    def receive(self):
        """
           receive() -> (message, src)
           
           Wait for SNMP message from remote SNMP process or timeout
           (and return a tuple of None's).

           Return a tuple of SNMP message (as string) and source address
           'src' (in socket module notation).
        """
        # Make sure the connection exists
        if not self.socket:
            raise error.NotConnected

        # Initialize sockets map
        r, w, x = [self.socket], [], []

        # Wait for response
        r, w, x = select.select(r, w, x, self.timeout)

        # Timeout occurred?
        if r:
            return self.read()

        # Return nothing on timeout
        return(None, None)

    def send_and_receive(self, message, dst=None):
        """
           send_and_receive(message[, dst]) -> (message, src)
           
           Send SNMP message to remote SNMP process by address specified on
           session object creation or 'dst' address and receive a response
           message or timeout (and raise NoResponse exception).

           Return a tuple of SNMP message (as string) and source address
           'src' (in socket module notation).
        """
        # Initialize retries counter
        retries = 0

        # Send request till response or retry counter hits the limit
        while retries < self.retries:
            # Send a request
            self.send(message, dst)

            # Wait for response
            (response, src) = self.receive()

            # See if it's succeeded
            if response:
                return(response, src)

            # Otherwise, try it again
            retries = retries + 1

        # No answer, raise an exception
        raise error.NoResponse('No response arrived before timeout')

    def close(self):
        """
           close()
           
           Close UDP socket used to communicate with remote SNMP agent.
        """
        # See if it's opened
        if self.socket:
            try:
                self.socket.close()

            except socket.error, why:
                raise error.TransportError('close() error: ' + str(why))

            # Initialize it to None to indicate it's closed
            self.socket = None  

class agent:
    """SNMP agent: receive SNMP request messages, reply with SNMP responses
    """
    def __init__(self, iface=('0.0.0.0', 161)):
        # For compatibility reasons, the first arg may also be a string
        if type(iface) == TupleType:
            self.iface = iface[0]
            self.port = iface[1]
        else:
            self.iface = iface
            self.port = 161

        # Block on select() waiting for request by default
        self.timeout = None
        
        # Initialize socket & default peer
        self.socket = None
        self.peer = None

    def __del__(self):
        """Close socket on object termination
        """
        try:
            self.close()

        except error.TransportError:
            pass

    def get_socket(self):
        """
           get_socket() -> socket

           Return socket object previously created with open() method.
        """
        return self.socket

    def open(self):
        """
           open()
           
           Initialize transport layer (UDP socket) to be used
           for further communication with remote SNMP process.
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        except socket.error, why:
            raise error.TransportError('socket() error: ' + str(why))

        # Bind to specific interface at SNMP agent machine
        try:
            self.socket.bind((self.iface, self.port))

        except socket.error, why:
            raise error.TransportError('bind() error: ' + str(why))

        return self.socket

    def send(self, message, dst=None):
        """
           send([message[, dst]])
           
           Send SNMP message (given as string) to remote SNMP process
           by source address of last received message (if any) or by 'dst'
           address given in socket module notation.
        """
        # Make sure the connection is established, open it otherwise
        if not self.socket:
            raise error.NotConnected

        # Destination must present
        if not dst and not self.peer:
            raise error.NoDestination('Message destination is not known')
        
        try:
            if dst:
                self.socket.sendto(message, dst)
            else:    
                self.socket.sendto(message, self.peer)
                
        except socket.error, why:
            raise error.TransportError('send() error: ' + str(why))

    def read(self):
        """
           read() -> (message, src)
           
           Read data from the socket (assuming there's some data ready
           for reading), return a tuple of SNMP message (as string) and
           source address 'src' (in socket module notation).
        """   
        # Make sure the connection exists
        if not self.socket:
            raise error.NotConnected

        try:
            (message, self.peer) = self.socket.recvfrom(65536)

        except socket.error, why:
            raise error.TransportError('recvfrom() error: ' + str(why))

        return (message, self.peer)
        
    def receive(self):
        """
           receive() -> (message, src)
           
           Wait for and receive SNMP message from a remote SNMP process
           or timeout (and return a tuple of None's).

           Return a tuple of SNMP message (as string) and source address
           'src' (in socket module notaton).
        """
        # Attempt to initialize transport stuff
        if not self.socket:
            self.open()
            
        # Initialize sockets map
        r, w, x = [self.socket], [], []

        # Wait for response
        r, w, x = select.select(r, w, x, self.timeout)

        # Timeout occurred?
        if r:
            return self.read()

        # Return nothing on timeout
        return (None, None)

    def receive_and_send(self, callback):
        """
           receive_and_send(callback)
           
           Wait for SNMP request from a remote SNMP process or timeout
           (and raise NoRequest exception), pass request to the callback
           function to build a response, send SNMP response back to
           remote SNMP process.
        """
        if not callable (callback):
            raise error.BadArgument('Bad callback function')

        while 1:
            # Wait for request to come
            (request, src) = self.receive()

            if not request:
                raise error.NoRequest('No request arrived before timeout')

            # Invoke callback function
            (response, dst) = callback(self, (request, src))

            # Send a response if any
            if (response):
                # Reply back by either source address or alternative
                # destination whenever given
                if dst:
                    self.send(response, dst)
                else:
                    self.send(response, src)

    def close(self):
        """
           close()
           
           Close UDP socket used to communicate with remote SNMP agent.
        """
        # See if it's opened
        if self.socket:
            try:
                self.socket.close()

            except socket.error, why:
                raise error.TransportError('close() error: ' + str(why))

            # Initialize it to None to indicate it's closed
            self.socket = None  

#
# Obsolete compatibility stuff
#

#class session(manager, message.manager, message.trap):
class session(manager):    
    """Just a compatibility stub. Use 'manager' or/and 'agent'
       classes instead!
    """
    def __init__(self, agent, community='public'):
        """Invoke superclasses constructors explicitly
        """
        manager.__init__(self, agent)
        message.manager.__init__(self, community)
        message.trap.__init__(self, community)         

    def send(self, message=None):
        """
           send([message])
           
           Send SNMP message (given as string) to remote SNMP process
           specified on session object creation.
        """
        manager.send(self, message)

    def read(self):
        """
           read() -> message
           
           Read data from the socket (assuming there's some data ready
           for reading), return SNMP message (as string).
        """   
        return manager.read(self)[0]
        
    def receive(self):
        """
           receive() -> message
           
           Wait for SNMP message from remote SNMP process or timeout
           (and return None).

           Return SNMP message (as string) otherwise.
        """
        manager.receive(self)[0]

    def send_and_receive(self, message):
        """
           send_and_receive(message) -> message
           
           Send SNMP message to remote SNMP process by address specified on
           session object creation and receive a response message or
           timeout (and raise NoResponse exception).

           Return SNMP message (as string) otherwise.
        """
        manager.send_and_receive(self, message)[0]
