from pysnmp.mapping import error

class TransportDispatcherBase:
    """Specifies mandatory transport API and some basic features
    """
    def __init__(self, **kwargs):
        self.doDispatchFlag = 1
        self.__transports = {}
        self.__appCbFun = None
        apply(self.registerTransports, [], kwargs)

    # Mapping object interface

    def __getattr__(self, attr):
        if attr in dir(self.__transports):
            return getattr(self.__transports, attr)
        raise AttributeError('%s object has no attr %s' % (self, attr))

    # Transport API
    
    def transportDispatcherSend(self, outgoingMessage, \
                          (transportDomain, transportAddress)):
        transport = self.get(transportDomain, None)
        if transport is None:
            raise error.BadArgumentError('Unknown transport domain %s' \
                                         % transportDomain)
        transport.transportDomainSend(outgoingMessage, transportAddress)

    def transportDispatcherRegisterCbFun(self, appCbFun):
        if self.__appCbFun is not None:
            raise error.BadArgumentError('Callback already registered')
        self.__appCbFun = appCbFun

    def transportDispatcherUnregisterCbFun(self):
        if self.__appCbFun is None:
            raise error.BadArgumentError('Callback not registered')
        self.__appCbFun = None
        
    def transportDispatcherDispatch(self, timeout=0.0):
        raise error.NotImplementedError('Method not implemented')

    def transportDispatcherClose(self):
        map(lambda x: x.transportDomainClose(), self.values())
        self.unregisterTransports()
        
    # Some basic functionality
    
    def registerTransports(self, **kwargs):
        for (name, transport) in kwargs.items():
            if self.has_key(name):
                raise error.BadArgumentError('Already registered %s' % name)
            transport.transportDomainOpen(self)
            transport.transportDomainRegisterCbFun(self.__cbFun)
            self[name] = transport

    def unregisterTransports(self):
        self.transportDispatcherUnregisterCbFun()
        self.clear()
        
    def __cbFun(self, (transportDomain, transportAddress), incomingMessage):
        for name, transport in self.items():
            if transport is transportDomain:
                transportDomain = name
                break
        else:
            raise error.BadArgumentError('Unregistered transport domain %s' \
                                         % transportDomain)

        if self.__appCbFun is not None:
            self.__appCbFun(self, (transportDomain, transportAddress), \
                            incomingMessage)
