"""Implements asyncore-based UDP transport domain"""
from socket import AF_INET
from types import TupleType
from pysnmp.carrier.asynsock.dgram.base import DgramSocketTransport

class UdpSocketTransport(DgramSocketTransport):
    sockFamily = AF_INET
    defaultPort = 161

    def rewriteAddress(self, transportAddress):
        if type(transportAddress) != TupleType:
            return transportAddress, self.defaultPort
        else:
            return transportAddress[0], transportAddress[1]
                    
