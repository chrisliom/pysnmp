"""
   Asynchronous SNMP manager class based on Sam Rushing's asyncore class.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
from types import ClassType
import sys, asyncore
from pysnmp.mapping.udp import role, error
from pysnmp.error import PySnmpError

class manager(asyncore.dispatcher):
    """An asynchronous SNMP manager based on the asyncore.py class.

       Send and receive UDP packets asynchronously.
    """
    def __init__(self, (cb_fun, cb_ctx), dst=(None, 0), iface=('0.0.0.0', 0)):
        # Make sure we get the callback function
        if not callable(cb_fun):
            raise error.BadArgumentError('Non-callable callback function')

        # Keep references to data and method objects supplied
        # by caller for callback on request completion.
        self.cb_fun = cb_fun
        self.cb_ctx = cb_ctx

        # Call parent classes constructor
        asyncore.dispatcher.__init__(self)

        # Create an instance of manager transport class
        self.manager = role.manager(dst, iface)

        # Create a socket and pass it to asyncore dispatcher
        self.set_socket(self.manager.open())

    def send(self, req, dst=(None, 0), (cb_fun, cb_ctx)=(None, None)):
        """
           send(req[, dst[, (cb_fun, cb_ctx)]])
           
           Send SNMP message (string) to remote server process as specified
           on manager object creation or by 'dst' address (given
           in socket module notation).

           The callback function (as specified on manager object creation)
           will be invoked on response arrival or error.
        """
        if cb_fun is not None:
            self.cb_fun = cb_fun
        if cb_ctx is not None:
            self.cb_ctx = cb_ctx
            
        self.manager.send(req, dst)

    def handle_read(self):
        """Overloaded asyncore method -- read SNMP reply message from
           socket.        

           This does NOT time out so one needs to implement a mean of
           handling timed out requests (see examples/async_snmp.py for
           one of possible solutions).
        """
        (response, src) = self.manager.read()

        # Pass SNMP response along with references to caller specified data
        # and ourselves
        self.cb_fun(self, self.cb_ctx, (response, src), (None, None, None))

    def writable(self):
        """Objects of this class never expect write events
        """
        return 0

    def handle_connect(self):
        """Objects of this class never expect connect events
        """
        pass

    def handle_close(self):
        """Invoked by asyncore on connection closed event
        """
        self.manager.close()

    def handle_error(self, exc_type=None, exc_value=None, exc_traceback=None):
        """Invoked by asyncore on any exception
        """
        # In modern Python distribution, the handle_error() does not receive
        # exception details
        if exc_type is None or exc_value is None or exc_traceback is None:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
        # In case of PySNMP exception, invoke the callback function
        # and pass it an empty result. Otherwise,just pass the exception on.
        if type(exc_type) == ClassType and \
           issubclass(exc_type, PySnmpError):
            self.cb_fun(self, self.cb_ctx,\
                        (None, None), (exc_type, exc_value, exc_traceback))
        else:
            raise

class agent(asyncore.dispatcher):
    """An asynchronous SNMP agent based on the asyncore.py class.

       Wait for and receive SNMP request messages, send SNMP response
       messages asynchronously.
    """
    def __init__(self, (cb_fun, cb_ctx), ifaces=[('0.0.0.0', 161)]):
        # Make sure we get the callback function
        if not callable(cb_fun):
            raise error.BadArgumentError('Non-callable callback function')

        # Keep references to data and method objects supplied
        # by caller for callback on request arrival.
        self.cb_fun = cb_fun
        self.cb_ctx = cb_ctx

        # Call parent class constructor
        asyncore.dispatcher.__init__(self)

        # Create an instance of SNMP agent transport class
        self.agent = role.agent(ifaces)

        # Create a socket and pass it to asyncore dispatcher.
        self.set_socket(self.agent.open())

    def send(self, rsp, dst):
        """
           send(message, dst)
           
           Send SNMP message (string) to remote SNMP process by 'dst' address
           (given in socket module notation).
        """
        self.agent.send(rsp, dst)

    def handle_read(self):
        """Overloaded asyncore method -- read SNMP message from socket.

           This does NOT time out so one needs to implement a mean of
           handling timed out requests (perhaps it's worth looking at
           medusa/event_loop.py for an interesting approach).
        """
        (request, src) = self.agent.read()

        # Pass SNMP request along with references to caller specified data
        # and ourselves
        self.cb_fun(self, self.cb_ctx, (request, src), (None, None, None))

    def writable(self):
        """Objects of this class never expect write events
        """
        return 0

    def handle_connect(self):
        """Objects of this class never expect connect events
        """
        pass

    def handle_close(self):
        """Invoked by asyncore on connection closed event
        """
        self.agent.close()

    def handle_error(self, exc_type=None, exc_value=None, exc_traceback=None):
        """Invoked by asyncore on any exception
        """
        # In modern Python distribution, the handle_error() does not receive
        # exception details
        if exc_type is None or exc_value is None or exc_traceback is None:
            exc_type, exc_value, exc_traceback = sys.exc_info()

        # In case of PySNMP exception, invoke the callback function
        # and pass it an empty result. Otherwise,just pass the exception on.
        if type(exc_type) == ClassType \
           and issubclass(exc_type, PySnmpError):
            self.cb_fun(self, self.cb_ctx,
                        (None, None), (exc_type, exc_value, exc_traceback))
        else:    
            raise
        
