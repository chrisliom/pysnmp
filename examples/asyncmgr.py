#!/usr/bin/env python
"""
   Implements a simple Telnet like server that interacts with user via
   command line. User instructs server to query arbitrary SNMP agent and
   report back to user when SNMP reply is received. Server may poll a
   number of SNMP agents in the same time as well as handle a number of
   user sessions simultaneously.

   Since MIB parser is not yet implemented in Python, this script takes and
   reports Object IDs in dotted numeric representation only.

   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
import sys, time, string, socket, getopt
from types import ClassType
import sys, asyncore, asynchat

from pysnmp.proto import v1, v2c
from pysnmp.asn1.error import ValueConstraintError
from pysnmp.mapping.udp import asynrole
import pysnmp.proto.api.generic
import pysnmp.proto.cli.ucd
from pysnmp.error import PySnmpError

# Initialize a dictionary of running telnet engines
global_engines = {}

class telnet_engine(asynchat.async_chat):
    """Telnet engine class. Implements command line user interface and
       SNMP request queue management.

       Each new SNMP request message context is put into a pool of pending
       requests. As response arrives, it's matched against each of pending
       message contexts.
    """
    class V1:
        """Just a name scope for v.1 specifics
        """
        reqTypes = { 'get' : v1.GetRequest, 'getnext': v1.GetNextRequest,
                     'set': v1.SetRequest, 'trap': v1.Trap }

    class V2c:
        """Just a name scope for v.2c specifics
        """
        reqTypes = { 'get': v2c.GetRequest, 'getnext': v2c.GetNextRequest,
                     'set': v2c.SetRequest, 'getbulk': v2c.GetBulkRequest,
                     'inform': v2c.InformRequest, 'report': v2c.Report,
                     'trap': v2c.SnmpV2Trap }
    
    def __init__ (self, sock):
        # Call constructor of the parent class
        asynchat.async_chat.__init__ (self, sock)

        # Set up input line terminator
        self.set_terminator ('\n')

        # Initialize input data buffer
        self.data = ''

        # Create async SNMP transport manager
        self.manager = asynrole.manager((self.request_done_fun, None))
        
        # A queue of pending requests
        self.pending = []

        # Register this instance of telnet engine at a global dictionary
        # used for their periodic invocations for timeout purposes
        global_engines[self] = 1

        # User interface goodies
        self.prompt = 'query> '
        self.welcome = 'Example Telnet server / SNMP manager ready.\n'

        # Commands help messages
        commands = 'Commands:\n'

        for ver in [ self.V1, self.V2c ]:
            commands = commands + '%s:\n' % ver.__name__
            for key in ver.reqTypes.keys():
                commands = commands + '  ' + '%-14s' % key + \
                           ' issue SNMP (%s) %s message\n' % \
                           (ver.__name__, ver.reqTypes[key].__name__)

        # Options help messages
        options =           'Options:\n'
        options = options + '  -h             this help screen.\n'
        options = options + '  -p <port>      port to communicate with at the agent. Default is 161.\n'
        options = options + '  -t <timeout>   response timeout. Default is 1.\n'
        options = options + '  -v <version>   SNMP protocol version. Default is 1.\n'
        specifics = 'Try \'help <command>\' for request-specific-params hints.'
        self.usage = 'Syntax: <command> [options] <snmp-agent> <request-specific-params>\n'
        self.usage = self.usage + commands + options + specifics

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

    def handle_error(self, exc_type=None, exc_value=None, exc_traceback=None):
        """Invoked by asyncore on any exception
        """
        # In modern Python distribution, the handle_error() does not receive
        # exception details
        if exc_type is None or exc_value is None or exc_traceback is None:
            exc_type, exc_value, exc_traceback = sys.exc_info()

        # In case of PySNMP exception, report it to user. Otherwise,
        # just pass the exception on.
        if type(exc_type) == ClassType and\
           issubclass(exc_type, PySnmpError):
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

        # Take the command
        cmd = args[0]

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

        # Handle special case -- help clause
        if cmd == 'quit':
            self.close()
        elif cmd == 'help':
            try:
                return eval('self.V' + version).reqTypes[args[0]]().cliUcdGetUsage()
            except KeyError:
                return 'Wrong SNMP message type for version %s: %s\n%s'\
                       % (version, args[0], self.usage)
            except IndexError:
                return 'No command to hint upon\n%s' % self.usage
                
        # Make sure we got enough arguments
        if len(args) < 1:
            return 'Insufficient number of arguments\n%s' % self.usage

        # Choose protocol version specific module
        try:
            req = eval('self.V' + version).reqTypes[cmd]()

        except (NameError, AttributeError):
            return 'Unsupported SNMP protocol version: %s\n%s'\
                   % (version, self.usage)

        except KeyError:
            return 'Wrong SNMP message type for version %s: %s\n%s'\
                   % (version, cmd, self.usage)
        
        # Initialize request message from C/L params
        try:
            req.cliUcdSetArgs(args[1:])
            
        except PySnmpError, why:
            return str(why)

        # ...transport layer to send it out
        self.manager.send(req.encode(), (args[0], port))
    
        # Add request details into a pool of pending requests (if needed)
        if hasattr(req, 'reply'):
            self.pending.append((req, (args[0], port), time.time() + timeout))
        
    def request_done_fun(self, manager, req, (answer, src),\
                         (exc_type, exc_value, exc_traceback)):
        """Callback method invoked by SNMP manager object as response
           arrives. Asynchronous SNMP manager object passes back a
           reference to object instance that initiated this SNMP request
           alone with SNMP response message.
        """
        if exc_type is not None:
            apply(self.handle_error, (exc_type, exc_value, exc_traceback))
            return
            
        # Initialize response buffer
        reply = 'Response from agent %s:\n' % str(src)

        # Decode response message
        for snmp in [ v2c, v1 ]:
            rsp = snmp.Response()
            try:
                rsp.decode(answer)
            except ValueConstraintError:
                continue
            break
        else:
            self.push('Inbound message dropped (unsupported protocol version?)\n'
                      + self.prompt)
            return

        # Walk over pending message context
        for (req, dst, expire) in self.pending:
            if req.match(rsp):
                # Take matched context off the pending pool
                self.pending.remove((req, dst, expire))

                break

        else:
            reply = reply +\
                    'WARNING: dropping unmatched (late) response: \n'\
                    + str(rsp)
            self.push(reply + self.prompt)
            return

        # Fetch Object ID's and associated values
        vars = rsp.apiGenGetPdu().apiGenGetVarBind()

        # Check for remote SNMP agent failure
        if rsp.apiGenGetPdu().apiGenGetErrorStatus():
            errorIndex = rsp.apiGenGetPdu().apiGenGetErrorIndex() - 1
            errorStatus = str(rsp['pdu'].values()[0]['error_status'])
            self.push(errorStatus)
            if errorIndex < len(vars):
                self.push(' at ' + str(vars[errorIndex][0]))

        # Convert two lists into a list of tuples and print 'em all
        for (oid, val) in vars:
            reply =  reply + '%s ---> %s\n' % (oid, val)

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
    # Initialize defaults
    telnetPort = 8989;
    
    # Initialize help messages
    options =           'Options:\n'
    options = options + '  -S <telnet-port> TCP port for telnet server to listen at. Default is %d.' % telnetPort
    usage = 'Usage: %s [options]\n' % sys.argv[0]
    usage = usage + options

    # Parse possible options
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], 'hS:',\
                                     ['help', 'telnet-port=' ])
    except getopt.error, why:
        print 'getopt error: %s\n%s' % (why, usage)
        sys.exit(-1)

    try:
        for opt in opts:
            if opt[0] == '-h' or opt[0] == '--help':
                print usage
                sys.exit(0)
            
            if opt[0] == '-S' or opt[0] == '--telnet-port':
                telnetPort = int(opt[1])

    except ValueError, why:
        print 'Bad parameter \'%s\' for option %s: %s\n%s' \
              % (opt[1], opt[0], why, usage)
        sys.exit(-1)

    if len(args) != 0:
        print 'Extra arguments supplied\n%s' % usage
        sys.exit(-1)

    # Create an instance of Telnet superserver
    server = telnet_server(telnetPort)

    # Start the select() I/O multiplexing loop
    while 1:
        # Deliver 'tick' event to every instance of telnet engine
        map(lambda x: x.tick(time.time()), global_engines.keys())

        # Do the I/O on active sockets
        asyncore.poll(1.0)
