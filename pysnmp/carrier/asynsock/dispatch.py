from asyncore import poll
from time import time
from pysnmp.carrier.base import AbstractTransportDispatcher

__all__ = [ 'AsynsockDispatcher' ]

class AsynsockDispatcher(AbstractTransportDispatcher):
    """Implements I/O over asynchronous sockets"""
    def __init__(self, **kwargs):
        self.__sockMap = {}
        self.timeout = 1.0
        apply(AbstractTransportDispatcher.__init__, [self], kwargs)

    def registerTransports(self, **kwargs):
        apply(AbstractTransportDispatcher.registerTransports, [self], kwargs)
        for transport in kwargs.values():
            transport.registerSocket(self.__sockMap)

    def unregisterTransports(self, *args):
        apply(
            AbstractTransportDispatcher.unregisterTransports, (self, ) + args
            )
        for name in args:
            transport.unregisterSocket()

    def runDispatcher(self, liveForever=1):
        self.doDispatchFlag = liveForever
        while 1:
            poll(self.timeout, self.__sockMap)
            self.handleTimerTick(time())
            if not self.doDispatchFlag:
                break
            
# XXX doDispatchFlag is needed?
