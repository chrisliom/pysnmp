from pysnmp.mapping import error

class TransportDomainBase:
    """Specifies mandatory API and implements some features of a
       SNMP transport domain
    """
    # mandatori API
    def transportDomainSend(self, outgoingMessage, transportAddress):
        raise error.NotImplementedError('Method not implemented')

    def transportDomainOpen(self, transportDispatcher):
        raise error.NotImplementedError('Method not implemented')

    def transportDomainClose(self):
        raise error.NotImplementedError('Method not implemented')

    def transportDomainRegisterCbFun(self, appCbFun):
        self._appCbFun = appCbFun

    def transportDomainUnregisterCbFun(self):
        self._appCbFun = None
        
