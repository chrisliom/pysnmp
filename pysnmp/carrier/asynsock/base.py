"""Defines standard API to asyncore-based transport"""
import socket, sys
from asyncore import dispatcher
from pysnmp.carrier import error

class AbstractSocketTransport(dispatcher):
    sockFamily = sockType = None
    retryCount = 0; retryInterval = 0
    def __init__(self):
        try:
            s = socket.socket(self.sockFamily, self.sockType)
        except socket.error, why:
            raise error.CarrierError('socket() failed: %s' % why)
        dispatcher.__init__(self, s)

    def registerSocket(self, sockMap=None):
        self.del_channel()
        self.add_channel(sockMap)
        
    def unregisterSocket(self, sockMap=None):
        self.del_channel(sockMap)
        
    # Public API
    
    def openClientMode(self, iface=None):
        raise error.NotImplementedError('Method not implemented')

    def openServerMode(self, iface=None):
        raise error.NotImplementedError('Method not implemented')
        
    def sendMessage(self, outgoingMessage, transportAddress):
        raise error.NotImplementedError('Method not implemented')

    def registerCbFun(self, cbFun):
        self._cbFun = cbFun

    def unregisterCbFun(self):
        self._cbFun = None

    def closeTransport(self):
        self.unregisterCbFun()
        self.close()
        
    # asyncore API
    def handle_close(self): raise error.CarrierError(
        'Transport unexpectedly closed'
        )
    def handle_error(self, *args): raise

