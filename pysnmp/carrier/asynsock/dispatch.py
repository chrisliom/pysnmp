from asyncore import poll
from time import time
from pysnmp.carrier.base import AbstractTransportDispatcher

__all__ = [ 'AsynsockDispatcher' ]

class AsynsockDispatcher(AbstractTransportDispatcher):
    """Implements I/O over asynchronous sockets"""
    def __init__(self, **kwargs):
        self.__sockMap = {}
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

    def runDispatcher(self, timeout=1.0):
        self.doDispatchFlag = 1
        while self.doDispatchFlag:
            poll(timeout, self.__sockMap)
            self.handleTimerTick(time())

# XXX doDispatchFlag is needed?
