import asyncore
from pysnmp.mapping.dispbase import TransportDispatcherBase

class SocketDispatcher(TransportDispatcherBase):
    """Implements meta I/O over asynchronous sockets
    """
    def __init__(self, **kwargs):
        self.socketMap = {}
        apply(TransportDispatcherBase.__init__, [self], kwargs)

    def transportDispatcherDispatch(self, timeout=1.0):
        self.doDispatchFlag = 1
        while self.doDispatchFlag: asyncore.poll(timeout, self.socketMap)
