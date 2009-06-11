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
# Description: Transport dispatcher based on twisted.internet.reactor

from time import time

from twisted.internet import reactor, task

from pysnmp.carrier.base import AbstractTransportDispatcher

class ReactorDispatcher(AbstractTransportDispatcher):
    """TransportDispatcher based on twisted.internet.reactor"""
    def __init__(self, *args, **kwargs):
        AbstractTransportDispatcher.__init__(self)

        self.timeout = 1
        if kwargs.has_key('timeout'):
            self.timeout = kwargs['timeout']

        self.loopingcall = task.LoopingCall(self.handleTimeout)

    def handleTimeout(self):
        self.handleTimerTick(time())

    def runDispatcher(self, timeout=0.0):
        if not reactor.running:
            reactor.run()

# jobstarted/jobfinished might be okay as-is

    def registerTransport(self, tDomain, transport):
        if not self.loopingcall.running and self.timeout > 0:
            self.loopingcall.start(self.timeout, now = False)
        AbstractTransportDispatcher.registerTransport(self, tDomain, transport)
        # Ugly, but we need to call handleTimerTick() asyncronously from transports now.
        # IOW, it is not possibile to call handleTimerTick after poll()ing every transport' socket
        transport.dispatcher = self

    def unregisterTransport(self, tDomain):
        t = AbstractTransportDispatcher.getTransport(self, tDomain)
        if t is not None:
            AbstractTransportDispatcher.unregisterTransport(self, tDomain)
            t.closeTransport()

        if len(self._AbstractTransportDispatcher__transports) == 0:
            # the last transport has been removed, stop the timeout
            if self.loopingcall.running:
                self.loopingcall.stop()
