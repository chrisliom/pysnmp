#!/usr/local/bin/python -O
"""
   Implements a simple Telnet like server that interacts with user via
   command line. User instructs server to query arbitrary SNMP agent and
   report back to user when SNMP reply is received. Server may poll a
   number of SNMP agents in the same time as well as handle a number of
   user sessions simultaneously.

   Since MIB parser is not yet implemented in Python, this script takes and
   reports Object IDs in dotted numeric representation only.

   Written by Ilya Etingof <ilya@glas.net>, 2000-2002.

"""
import time
import string
import socket
from types import ClassType
import asyncore
import asynchat
import getopt

# Import PySNMP modules
from pysnmp import asn1, v1, v2c
from pysnmp import asynrole, error

# Initialize a dictionary of running telnet engines
global_engines = {}

class telnet_engine(asynchat.async_chat):
    """Telnet engine class. Implements command line user interface and
       SNMP request queue management.

       Each new SNMP request message context is put into a pool of pending
       requests. As response arrives, it's matched against each of pending
       message contexts.
    """
    def __init__ (self, sock):
        # Call constructor of the parent class
        asynchat.async_chat.__init__ (self, sock)

        # Set up input line terminator
        self.set_terminator ('\n')

        # Initialize input data buffer
        self.data = ''

        # Create async SNMP transport manager
        self.manager = asynrole.manager(self.request_done_fun)
        
        # A queue of pending requests
        self.pending = []

        # Run our own source of SNMP message serial number to preserve its
        # sequentiality
        self.request_id = 1

        # Register this instance of telnet engine at a global dictionary
        # used for their periodic invocations for timeout purposes
        global_engines[self] = 1

        # User interface goodies
        self.prompt = 'query> '
        self.welcome = 'Example Telnet server / SNMP manager ready.\n'

        # Commands help messages
        commands =            'Commands:\n'

        for mod in (v1, v2c):
            rtypes = dir(mod)
            for rtype in rtypes:
                if rtype[-7:] == 'REQUEST':
                    commands = commands + '  ' + '%-14s' % rtype[:-7] + \
                               ' issue SNMP (%s) %s request\n' % \
                               (mod.__name__[7:], rtype[:-7])

        # Options help messages
        options =           'Options:\n'
        options = options + '  -p <port>      port to communicate with at the agent. Default is 161.\n'
        options = options + '  -t <timeout>   response timeout. Default is 1.'
        self.usage = 'Syntax: <command> [options] <snmp-agent> <community> <obj-id [[obj-id] ... ]\n'
        self.usage = self.usage + commands + options

        # Send welcome message down to user. By using push() method we
        # having asynchronous engine delivering welcome message to user.
        self.push(self.welcome + self.usage + '\n' + self.prompt)

    def collect_incoming_data (self, data):
        """Put data read from socket to a buffer
        """
        # Collect data in input buffer
        self.data = self.data + data

    def found_terminator (self):
        """This method is called by asynchronous engine when it finds
           command terminator in the input stream
        """   
        # Take the complete line and reset input buffer
        line = self.data
        self.data = ''

        # Handle user command
        response = self.process_command(line)

        # Reply back to user whenever there is anything to reply
        if response:
            self.push(response + '\n')

        self.push(self.prompt)

    def handle_error(self, exc_type, exc_value, exc_traceback):
        """Invoked by asyncore on any exception
        """
        # In case of PySNMP exception, report it to user. Otherwise,
        # just pass the exception on.
        if type(exc_type) == ClassType and\
           issubclass(exc_type, error.General):
            self.push('Exception: %s: %s\n' % (exc_type, exc_value))
        else:
            raise (exc_type, exc_value)
        
    def handle_close(self):
        """Invoked by asyncore on connection termination
        """
        # Get this instance of telnet engine off the global pool
        del global_engines[self]
        
        # Pass connection close event to accompanying asyncore objects
        self.manager.close()
        asynchat.async_chat.close(self)
        
    def process_command (self, line):
        """Process user input
        """
        # Initialize defaults
        port = 161
        timeout = 1
        version = '1'

        # Split request up to fields
        args = string.split(line)

        # Make sure request is not empty
        if not args:
            return

        # Parse command
        cmd = string.upper(args[0])

        # Parse possible options
        try:
            (opts, args) = getopt.getopt(args[1:], 'hp:t:v:',\
                                         ['help', 'port=', \
                                          'version=', 'timeout='])
        except getopt.error, why:
            return 'getopt error: %s\n%s' % (why, self.usage)

        try:
            for opt in opts:
                if opt[0] == '-h' or opt[0] == '--help':
                    return self.usage
            
                if opt[0] == '-p' or opt[0] == '--port':
                    port = int(opt[1])

                if opt[0] == '-t' or opt[0] == '--timeout':
                    timeout = int(opt[1])

                if opt[0] == '-v' or opt[0] == '--version':
                    version = opt[1]

        except ValueError, why:
            return 'Bad parameter \'%s\' for option %s: %s\n%s' \
                   % (opt[1], opt[0], why, self.usage)
            
        # Make sure we got enough arguments
        if len(args) < 3:
            return 'Insufficient number of arguments\n%s' % self.usage

        # Create a SNMP request&response objects from protocol version
        # specific module.
        try:
            req = eval('v' + version + '.' + cmd + 'REQUEST')()

        except (NameError, AttributeError):
            return 'Unsupported SNMP protocol version/request type: %s/%s\n%s'\
                   % (version, cmd, self.usage)

        # Update request ID
        self.request_id = self.request_id + 1

        # Build complete SNMP request message and pass it over to
        # transport layer to send it out
        self.manager.send(req.encode(request_id=self.request_id,\
                                     community=args[1], \
                                     encoded_oids=map(asn1.OBJECTID().encode,\
                                                      args[2:])),\
                          (args[0], port))
            
        # Add request details into a pool of pending requests
        self.pending.append((req, (args[0], port), time.time() + timeout))
        
    def request_done_fun(self, manager, data, (response, src), exp):
        """Callback method invoked by SNMP manager object as response
           arrives. Asynchronous SNMP manager object passes back a
           reference to object instance that initiated this SNMP request
           alone with SNMP response message.
        """
        if exp[0] is not None:
            apply(self.handle_error, exp)
            return
            
        # Initialize response buffer
        reply = 'Response from agent %s:\n' % str(src)

        # Decode response message
        (rsp, rest) = v2c.decode(response)
        
        # Walk over pending message context
        for (req, dst, expire) in self.pending:
            if req == rsp:
                # Take matched context off the pending pool
                self.pending.remove((req, dst, expire))

                break

        else:
            reply = reply +\
                    'WARNING: dropping unmatched (late) response: \n'\
                    + str(rsp)
            self.push(reply + self.prompt)
            return

        # Decode BER encoded Object IDs.
        oids = map(lambda x: x[0], map(asn1.OBJECTID().decode, \
                                       rsp['encoded_oids']))

        # Decode BER encoded values associated with Object IDs.
        vals = map(lambda x: x[0](), map(asn1.decode, rsp['encoded_vals']))

        # Convert two lists into a list of tuples and print 'em all
        for (oid, val) in map(None, oids, vals):
            reply =  reply + oid + ' ---> ' + str(val) + '\n'

        # Send reply back to user
        self.push(reply + self.prompt)

    def tick(self, now):
        """This method gets invoked periodically from upper scope for
           generic housekeeping purposes.
        """
        # Walk over pending message context
        for (req, dst, expire) in self.pending:
            # Expire long pending contexts
            if expire < now:
                # Send a notice on expired request context
                self.push('WARNING: expiring long pending request %s destined %s\n' % (req, dst))

                # Expire context
                self.pending.remove((req, dst, expire))
        
class telnet_server(asyncore.dispatcher):
    """Telnet server class. Listens for incoming requests and creates
       instances of telnet engine classes for handling new session.
    """
    def __init__(self, port=8989):
        """Takes optional TCP port number for the server to bind to.
        """
        # Call parent class constructor explicitly
        asyncore.dispatcher.__init__(self)
        
        # Create socket of requested type
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set it to re-use address
        self.set_reuse_addr()
        
        # Bind to all interfaces of this host at specified port
        self.bind(('', port))
        
        # Start listening for incoming requests
        self.listen(5)

    def handle_accept(self):
        """Called by asyncore engine when new connection arrives
        """
        # Accept new connection
        (sock, addr) = self.accept()

        # Create an instance of Telnet engine class to handle this new user
        # session and pass it socket object to use any further
        telnet_engine(sock)

# Run the module if it's invoked for execution
if __name__ == '__main__':
    # Create an instance of Telnet superserver
    server = telnet_server ()

    # Start the select() I/O multiplexing loop
    while 1:
        # Deliver 'tick' event to every instance of telnet engine
        map(lambda x: x.tick(time.time()), global_engines.keys())

        # Do the I/O on active sockets
        asyncore.poll(1.0)
