import socket
from pysnmp.mapping.sockbase import SocketBase

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
        self.__appCbFun((self, transportAddress), incomingMessage)

class UdpDomainManager(UdpDomain):
    def __init__(self, transport, transportAddress=None):
        UdpDomain.__init__(self, transport)
        self.transportAddress=transportAddress

    def send(self, outgoingMessage, transportAddress=None):
        if transportAddress is None:
            transportAddress = self.transportAddress
        UdpDomain.send(self, outgoingMessage, transportAddress)
             
class UdpDomainAgent(UdpDomain):
    def __init__(self, transport, iface=('0.0.0.0', 161)):
        UdpDomain.__init__(self, transport)
        try:
            self.bind(iface)
        except socket.error, why:
            raise error.NetworkError('bind() failed: ' + why)
