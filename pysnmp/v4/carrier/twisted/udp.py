#!/usr/bin/env python
#
# Copyright (c) 2009, Truelite Srl <info@truelite.it>, all rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#   * The name of the authors may not be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
# Author: Filippo Giunchedi <filippo@truelite.it>
# Description: twisted DatagramProtocol UDP transport

from time import time

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol

from pysnmp.carrier import error

class ReactorUDPTransport(DatagramProtocol):
    """UDP Transport based on twisted, to be used with ReactorDispatcher"""

    def __init__(self):
        self.__writeQ = []

# twisted API
    def datagramReceived(self, datagram, address):
        if self._cbFun is not None:
            self._cbFun(self, address, datagram)
        else:
            raise error.CarrierError('Unable to call cbFun')

        if self.dispatcher is not None:
            self.dispatcher.handleTimerTick(time())
        else:
            raise error.CarrierError('Unable to call handleTimerTick')

    def startProtocol(self):
        while self.__writeQ:
            msg, addr = self.__writeQ.pop(0)
            self.transport.write(msg, addr)

    def stopProtocol(self):
        self.unregisterCbFun()
        self.dispatcher = None

# asyncore AbstractSocketTransport API
    def openClientMode(self, iface=''):
        self._lport = reactor.listenUDP(0, self, iface)
        return self

    def openServerMode(self, iface=None):
        self._lport = reactor.listenUDP(iface[1], self, iface[0])
        return self

    def sendMessage(self, outgoingMessage, transportAddress):
        if self.transport is None:
            self.__writeQ.append((outgoingMessage, transportAddress))
        else:
            self.transport.write(outgoingMessage, transportAddress)

    def registerCbFun(self, cbFun):
        self._cbFun = cbFun

    def unregisterCbFun(self):
        self._cbFun = None

    def closeTransport(self):
        self.transport.stopListening()
