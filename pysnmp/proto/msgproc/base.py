from pysnmp.proto.msgproc import error

class AbstractMessageProcessingModel:
    __stateReference = 0L
    def __init__(self, mibInstrController=None):
        self.mibInstrController = mibInstrController
        self.__msgIdIndex = {}
        self.__stateReferenceIndex = {}
        # Message expiration mechanics
        self.__expirationQueue = {}
        self.__expirationTimer = 0L
    
    def prepareOutgoingMessage(self, **kwargs): pass
    def prepareResponseMessage(self, **kwargs): pass
    def prepareDataElements(self, wholeMsg): pass

    def _newStateReference(self):
        AbstractMessageProcessingModel.__stateReference = (
            AbstractMessageProcessingModel.__stateReference + 1
            )
        return self.__stateReference

    # Server mode cache handling

    def _cachePushByStateRef(self, stateReference, **kwargs):
        if self.__stateReferenceIndex.has_key(stateReference):
            raise error.MessageProcessingModelError(
                'Cache dup for stateReference=%s at %s' %
                (stateReference, self)
                )
        self.__stateReferenceIndex[stateReference] = kwargs
        # Schedule to expire
        if self.__expirationQueue.has_key(self.__expirationTimer+50):
            self.__expirationQueue[self.__expirationTimer+50].append(kwargs)
        else:
            self.__expirationQueue[self.__expirationTimer+50] = [ kwargs ]
        self.__expireCaches()
        
    def _cachePopByStateRef(self, stateReference):
        cachedInfo = self.__stateReferenceIndex.get(stateReference)
        if cachedInfo is None:
            raise error.MessageProcessingModelError(
                'Cache miss for stateReference=%s at %s' %
                (stateReference, self)
                )
        del self.__stateReferenceIndex[stateReference]
        return cachedInfo

    # Client mode cache handling

    def _cachePushByMsgId(self, msgId, **kwargs):
        if self.__msgIdIndex.has_key(msgId):
            raise error.MessageProcessingModelError(
                'Cache dup for msgId=%s at %s' % (msgId, self)
                )
        self.__msgIdIndex[msgId] = kwargs
        # Schedule to expire
        if self.__expirationQueue.has_key(self.__expirationTimer+50):
            self.__expirationQueue[self.__expirationTimer+50].append(kwargs)
        else:
            self.__expirationQueue[self.__expirationTimer+50] = [ kwargs ]
        self.__expireCaches()
        
    def _cachePopByMsgId(self, msgId):
        cachedInfo = self.__msgIdIndex.get(msgId)
        if cachedInfo is None:
            raise error.MessageProcessingModelError(
                'Cache miss for msgId=%s at %s' % (msgId, self)
                )
        del self.__msgIdIndex[msgId]
        return cachedInfo

    def __expireCaches(self):
        # Uses internal clock to expire pending messages
        if self.__expirationQueue.has_key(self.__expirationTimer):
            del self.__expirationQueue[self.__expirationTimer]
        self.__expirationTimer = self.__expirationTimer + 1
