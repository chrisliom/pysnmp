from pysnmp.proto.secmod import error

class AbstractSecurityModel:
    def __init__(self, mibInstrController=None):
        self.mibInstrController = mibInstrController
        self.__cacheEntries = {}
    
    def processIncomingMsg(self, msg, **kwargs):
        raise error.NotImplementedError(
            'Security model %s not implemented' % self
            )

    def generateRequestMsg(self, msg, **kwargs):
        raise error.NotImplementedError(
            'Security model %s not implemented' % self
            )

    def generateResponseMsg(self, msg, **kwargs):
        raise error.NotImplementedError(
            'Security model %s not implemented' % self
            )
