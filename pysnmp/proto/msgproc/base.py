# MP-specific cache management
from pysnmp.proto.msgproc import error

class AbstractMessageProcessingModel:
    __stateReference = 0L
    def __init__(self, mibInstrumController=None):
        self.mibInstrumController = mibInstrumController
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
        expireAt = self.__expirationTimer+50
        self.__stateReferenceIndex[stateReference] = ( kwargs, expireAt )

        # Schedule to expire
        if not self.__expirationQueue.has_key(expireAt):
            self.__expirationQueue[expireAt] = {}
        if not self.__expirationQueue[expireAt].has_key('stateReference'):
            self.__expirationQueue[expireAt]['stateReference'] = {}
        self.__expirationQueue[expireAt]['stateReference'][stateReference] = 1
        self.__expireCaches()
        
    def _cachePopByStateRef(self, stateReference):
        cacheInfo = self.__stateReferenceIndex.get(stateReference)
        if cacheInfo is None:
            raise error.MessageProcessingModelError(
                'Cache miss for stateReference=%s at %s' %
                (stateReference, self)
                )
        del self.__stateReferenceIndex[stateReference]
        cacheEntry, expireAt = cacheInfo
        del self.__expirationQueue[expireAt]['stateReference'][stateReference]
        return cacheEntry

    # Client mode cache handling

    def _cachePushByMsgId(self, msgId, **kwargs):
        if self.__msgIdIndex.has_key(msgId):
            raise error.MessageProcessingModelError(
                'Cache dup for msgId=%s at %s' % (msgId, self)
                )
        expireAt = self.__expirationTimer+50
        self.__msgIdIndex[msgId] = ( kwargs, expireAt )
        
        # Schedule to expire
        if not self.__expirationQueue.has_key(expireAt):
            self.__expirationQueue[expireAt] = {}
        if not self.__expirationQueue[expireAt].has_key('msgId'):
            self.__expirationQueue[expireAt]['msgId'] = {}
        self.__expirationQueue[expireAt]['msgId'][msgId] = 1
        self.__expireCaches()
        
    def _cachePopByMsgId(self, msgId):
        cacheInfo = self.__msgIdIndex.get(msgId)
        if cacheInfo is None:
            raise error.MessageProcessingModelError(
                'Cache miss for msgId=%s at %s' % (msgId, self)
                )
        del self.__msgIdIndex[msgId]
        cacheEntry, expireAt = cacheInfo
        del self.__expirationQueue[expireAt]['msgId'][msgId]
        return cacheEntry

    def __expireCaches(self):
        # Uses internal clock to expire pending messages
        if self.__expirationQueue.has_key(self.__expirationTimer):
            cacheInfo = self.__expirationQueue[self.__expirationTimer]
            if cacheInfo.has_key('stateReference'):
                for stateReference in cacheInfo['stateReference']:
                    del self.__stateReferenceIndex[stateReference]
            if cacheInfo.has_key('msgId'):
                for msgId in cacheInfo['msgId']:
                    del self.__msgIdIndex[msgId]
            del self.__expirationQueue[self.__expirationTimer]
        self.__expirationTimer = self.__expirationTimer + 1
