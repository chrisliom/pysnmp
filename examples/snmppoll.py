#!/usr/local/bin/python -O
"""
   Retrieve MIB variables associated with user specifed SNMP Object IDs
   from multiple SNMP agents at once by running dedicated SNMP engine
   for each destination.

   The number of simultaneous SNMP sessions is limited by the maximum number
   of file descriptors available to the process.

   Since MIB parser is not yet implemented in Python, this script takes and
   reports Object IDs in dotted numeric representation only.

   Written by Ilya Etingof <ilya@glas.net>, 2000-2002.

"""
# Import PySNMP modules
from pysnmp import asn1, v1, v2c
from pysnmp import role

class snmppoll (msession.manager):
    """Collect SNMP "GETREQUEST" messages, then issue them all at once
       through individual sockets and wait for replies to come back.

       Report reply messages back to caller in exactly the same order
       as requests were submitted.
    """
    def __init__(self):
        """Invoke overloaded class constructors.
        """
        msession.manager.__init__(self)
        self.initialize()

    def initialize (self):
        """Purge and initialize internal queue of pending requests.
        """
        # [Re-]create a list of active sessions
        self.sessions = []

        # Invoke overloaded superclass method
        msession.manager.initialize(self)
        
    def submit(self, agent, community, oids):
        """
           submit(agent, community, oids):

           Create SNMP message of type "GETREQUEST" with SNMP community
           name "community" and payload Object IDs "oids". Then destine
           message to SNMP process at "agent" and store message details
           at an internal queue.

           All previously queued messages are sent upon dispatch() method
           invocation.

        """
        # Create new SNMP request message context
        mctx = message.manager(community)

        # BER encode SNMP Object IDs and create corresponding
        # list of [empty] encoded values.
        encoded_oids = map(mctx.encode_oid, map(mctx.str2nums, oids))
        encoded_vals = [ None ] * len(encoded_oids)
        
        # Complete SNMP message and submit it to multisession dispatcher
        msession.manager.submit(self, agent,\
                                mctx.encode_request('GETREQUEST',\
                                                    encoded_oids,\
                                                    encoded_vals))

        # Store request message context alone with destination
        # address for further reference
        self.sessions.append((mctx, agent))

    def retrieve (self):
        """
           retrieve() -> [(oids, vals, src), ...]
           
           Retrieve previously received SNMP responses as a list of tuples
           of Object IDs, their associated values and source address.

           Unsuccessful requests are indicated by None's in Object ID's and
           their values.
        """
        # Retrieve a list of responses from multisession dispatcher
        responses = msession.manager.retrieve(self)

        results = []
        
        # Walk over the list of stored requests contexts
        for (mctx, dst) in self.sessions:
            # Assume request failure so there will be no data to return
            oids = [ None ]
            vals = [ None ]

            # Pick matching response
            response = responses[self.sessions.index((mctx, dst))]

            # Try to decode response for this session whenever present
            if response:
                try:
                    # Decode response message
                    encoded_pairs = mctx.decode_response(response[0])
                    oids = map(mctx.decode_value, encoded_pairs[0])
                    vals = map(mctx.decode_value, encoded_pairs[1])

                except error.SNMPError:
                    pass

            results.append((oids, vals, dst))
            
        return results

# Run the module if it's invoked for execution
if __name__ == '__main__':
    import sys
    import string
    import getopt

    # Initialize help messages
    options =           'Options:\n'
    options = options + '  -p <port>      port to communicate with at the agent. Default is 161.\n'
    options = options + '  -r <retries>   number of retries to be used in requests. Default is 5.\n'
    options = options + '  -t <timeout>   timeout between retries. Default is 1.\n'
    options = options + '  -i <filename>  file to read additional args from. Use \'stdin\' for stdin.'
    usage = 'Usage: %s [options] <snmp-agent> <community> <obj-id [[obj-id] ... ]\n' % sys.argv[0]
    usage = usage + options
    
    # Initialize defaults
    port = 161
    retries = 5
    timeout = 1
    input = None
    
    # Parse possible options
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], 'p:r:t:i:',\
                                     ['port=', 'retries=', 'timeout=',\
                                      'input='])
    except getopt.error, why:
        print 'getopt error: %s\n%s' % (why, usage)
        sys.exit(-1)

    for opt in opts:
        if opt[0] == '-p' or opt[0] == '--port':
            try:
                port = int(opt[1])

            except ValueError, why:
                print 'Bad port: %s\n%s' % (why, usage)
                sys.exit(-1)

        if opt[0] == '-r' or opt[0] == '--retries':
            try:
                retries = int(opt[1])

            except ValueError, why:
                print 'Bad retries: %s\n%s' % (why, usage)
                sys.exit(-1)

        if opt[0] == '-t' or opt[0] == '--timeout':
            try:
                timeout = int(opt[1])

            except ValueError, why:
                print 'Bad timeout: %s\n%s' % (why, usage)
                sys.exit(-1)
            
        if opt[0] == '-i' or opt[0] == '--input':
            input = opt[1]

    if len(args) < 3:
        print 'Insufficient number of arguments supplied\n%s' % usage
        sys.exit(-1)

    ctx = snmppoll()

    # Commit options
    ctx.retries = retries
    ctx.timeout = timeout
    
    # Submit SNMP request details (taken from command line)
    ctx.submit((args[0], port), args[1], args[2:])

    # Read additional SNMP requests details from file
    if input:
        # Can also read from stdin
        if input == 'stdin':
            f = sys.stdin
        else:
            try:
                f = open(input)

            except IOError, why:
                print 'open() failed: %s\n%s' % (why, usage)
                sys.exit(-1)

        while 1:
            line = f.readline()

            if not line:
                break

            args = string.split(line)

            if len(args) < 3:
                print 'Insufficient number of arguments at line: \'%s\'\n%s'\
                      % (line, usage)
                sys.exit(-1)

            # Submit SNMP request details (taken from file)
            ctx.submit((args[0], port), args[1], args[2:])

    # Run the I/O engine
    ctx.dispatch()

    # Fetch responses from multisession manager
    for (oids, vals, src) in ctx.retrieve():
        # ...and print them out
        for (oid, val) in map(None, oids, vals):
            print str(src) + ': ',
            if oid:
                print str(oid) + ' ---> ' + str(val)
            else:
                print 'Timed out'
