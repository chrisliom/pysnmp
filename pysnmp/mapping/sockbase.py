import asyncore, socket
from pysnmp.mapping.tranbase import TransportDomainBase
from pysnmp.mapping import error

class SocketBase(TransportDomainBase, asyncore.dispatcher):
    def __init__(self, sockFamily, sockType):
        self.sockFamily, self.sockType = (sockFamily, sockType)
        self.timeout = 3
        self.retries = 2

    # transport domain API
        
    def transportDomainOpen(self, transportDispatcher):
        try:
            s = socket.socket(self.sockFamily, self.sockType)
        except socket.error, why:
            raise error.NetworkError('socket() failed: ' + why)
        else:
            asyncore.dispatcher.__init__(self, s, \
                                         transportDispatcher.socketMap)

    def transportDomainClose(self):
        self.transportDispatcher = None
        
    # asyncore API
    
    def writable(self): return 0
    
    def handle_connect(self): return
    
    def handle_close(self): self.transportDomainClose()

    def handle_error(self, *args):
        self.__appCbFun((self, None), sys.exc_info())

    def getTimeout(self): return self.timeout
    def getRetries(self): return self.retries
