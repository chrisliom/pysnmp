import socket
from pysnmp.mapping.sockbase import SocketBase
from pysnmp.mapping.udp.error import NetworkError

class UdpDomain(SocketBase):
    def __init__(self):
        SocketBase.__init__(self, socket.AF_INET, socket.SOCK_DGRAM)

    def transportDomainSend(self, outgoingMessage, transportAddress):
        try:
            self.socket.sendto(outgoingMessage, 0, transportAddress)
        except socket.error:
            self.transportDispatcher.cbFun((self, None), sys.exc_info())

    def handle_read(self):
        (incomingMessage, transportAddress) = self.socket.recvfrom(65535)
        self._appCbFun((self, transportAddress), incomingMessage)

class UdpDomainAgent(UdpDomain):
    def __init__(self, iface=('0.0.0.0', 161)):
        UdpDomain.__init__(self)
        self._iface = iface

    def transportDomainOpen(self, transportDispatcher):
        SocketBase.transportDomainOpen(self, transportDispatcher)
        try:
            self.bind(self._iface)
        except socket.error, why:
            raise NetworkError('bind() failed: %s' % why)
    
class UdpDomainManager(UdpDomainAgent):
    def __init__(self, transportAddress=None, iface=('0.0.0.0', 0)):
        UdpDomainAgent.__init__(self, iface)
        self._transportAddress = transportAddress

    def transportDomainSend(self, outgoingMessage, transportAddress=None):
        if transportAddress is None:
            transportAddress = self._transportAddress
        UdpDomainAgent.transportDomainSend(self, outgoingMessage, transportAddress)
