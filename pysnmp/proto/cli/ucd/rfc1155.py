"""
   UCD-SNMP-style command line interface to rfc1155 objects

   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'IpAddressMixIn' ]

import string
from pysnmp.error import PySnmpError
from pysnmp.proto import rfc1155
from pysnmp.proto.cli import error

class OptsParser:
    cliUcdOptId = None
    cliUcdOptValName = 'value'
    cliUcdOptBraces = ('[ ', ' ]')
    cliUcdOptValBraces = ('<', '>')
    cliUcdOptFilter = lambda x, y: y
    
    def cliUcdGetUsage(self):
        if self.cliUcdOptId is None:
            return ''
        u = ''
        if self.cliUcdOptId and self.cliUcdOptId[-1] == ':':
            u = u + self.cliUcdOptBraces[0] + self.cliUcdOptId[:-1] + ' '
        u = u + self.cliUcdOptValBraces[0] + \
            self.cliUcdOptValName + self.cliUcdOptValBraces[1]
        if self.cliUcdOptId and self.cliUcdOptId[-1] == ':':
            u = u + self.cliUcdOptBraces[1]
        return u
        
    def cliUcdGetOptsUsage(self, ident=''):
        if self.cliUcdOptId is None:
            return ident
        if self.cliUcdOptId == '':
            return ident + '%-15s -- initializes %s from %s value' % \
                   (self.cliUcdOptValName, self.__class__.__name__,
                    self.cliUcdOptValName)
        if self.cliUcdOptId[-1] == ':':
            return ident + '%-3s %-12s -- initializes %s from %s value' % \
                   (self.cliUcdOptId[:-1], self.cliUcdOptValName,
                    self.__class__.__name__, self.cliUcdOptValName)
        else:
            return ident + '%-15s -- sets \'%s\' to true at %s' % \
                   (self.cliUcdOptValName, self.__class__.__name__)
        
    def cliUcdSetArgs(self, argv):
        """Syntax: [-][sw][:] [val]
           Where:
                   -   -- position-independend option
                   sw  -- option ID
                   :   -- option value expected
                   val -- value
        """
        if self.cliUcdOptId is None or not len(argv):
            return list(argv)
        valFollowsFlag = noSwitchFlag = posFreeFlag = None
        opt = self.cliUcdOptId
        if opt == '':
            noSwitchFlag = 1
        else:
            if opt[-1] == ':':
                valFollowsFlag = 1; opt = opt[:-1]
            if opt[0] == '-':
                posFreeFlag = 1
        idx = 0; newArgv = []
        while idx < len(argv):
            if noSwitchFlag or valFollowsFlag and opt == argv[idx]:
                if idx == 0 or posFreeFlag:
                    if noSwitchFlag:
                        val = argv[idx]
                    elif valFollowsFlag:
                        if idx >= len(argv):
                            raise error.BadArgumentError('Missing option at %s: %s' % (self.__class__.__name__, argv[idx+1:]))
                        idx = idx + 1
                        val = argv[idx]
                    else:
                        val = not None
                    try:
                        val = self.cliUcdOptFilter(val)
                    except StandardError, why:
                        raise error.BadArgumentError('Value convertion error at %s: %s: %s' % (self.__class__.__name__, val, why))                        
                    try:
                        self.set(val)
                    except Exception, why:
                        raise error.BadArgumentError('Parser error at %s: %s: %s' % (self.__class__.__name__, argv[idx], why))
                    idx = idx + 1
                    continue
            newArgv.append(argv[idx])
            idx = idx + 1
        return newArgv

class IntegerMixIn(OptsParser):
    cliUcdOptId = 'i:'
    cliUcdOptValName = 'integer'
    cliUcdOptFilter = lambda x, y: string.atol(y)

class OctetStringMixIn(OptsParser):    
    cliUcdOptId = 's:'
    cliUcdOptValName = 'string'
    
class NullMixIn(OptsParser):
    cliUcdOptId = 'n:'
    cliUcdOptValName = 'null'

class ObjectIdentifierMixIn(OptsParser):
    cliUcdOptId = 'o:'
    cliUcdOptValName = 'OID'

class IpAddressMixIn(OptsParser):
    cliUcdOptId = 'a:'
    cliUcdOptValName = 'ipaddr'

class CounterMixIn(IntegerMixIn):
    cliUcdOptId = 'c:'
    cliUcdOptValName = 'counter'

class GaugeMixIn(IntegerMixIn):
    cliUcdOptId = 'g:'
    cliUcdOptValName = 'gauge'
    
class TimeTicksMixIn(IntegerMixIn):
    cliUcdOptId = 't:'
    cliUcdOptValName = 'timeticks'

class SequenceMixIn:
    cliUcdOptBraces = ('', '')
    def cliUcdGetUsage(self):
        u = ''
        for comp in self.fixedComponents:
            if hasattr(comp, 'cliUcdGetUsage'):
                s = comp().cliUcdGetUsage()
                if s:
                    u = u + ' ' + s
        return self.cliUcdOptBraces[0] + u + self.cliUcdOptBraces[1]

    def cliUcdGetOptsUsage(self, ident=''):
        u = ident+'%s initialization:' % self.__class__.__name__
        for comp in self.fixedComponents:
            if hasattr(comp, 'cliUcdGetUsage'):
                s = comp().cliUcdGetOptsUsage(ident+' ')
                if len(string.strip(s)):
                    u = u + '\n' + ident + s
        return u

    def cliUcdSetArgs(self, argv):
        for comp in self.fixedComponents:
            if hasattr(comp, 'cliUcdSetArgs'):
                val = comp()
                newArgv = val.cliUcdSetArgs(argv)
                if len(newArgv) != len(argv):
                    # XXX
                    self[self.fixedNames[self.fixedComponents.index(comp)]] = val
                argv = newArgv
        return argv

class SequenceOfMixIn:
    cliUcdOptBraces = ('', '')
    def cliUcdGetUsage(self):
        u = ''
        if hasattr(self.protoComponent, 'cliUcdGetUsage'):
            s = self.protoComponent().cliUcdGetUsage()
            if len(string.strip(s)):
                u = s + ' ...'
        return self.cliUcdOptBraces[0] + u + ' ' + self.cliUcdOptBraces[1]

    def cliUcdGetOptsUsage(self, ident=''):
        u = ident+'%s initialization:' % self.__class__.__name__
        if hasattr(self.protoComponent, 'cliUcdGetOptsUsage'):
            s = self.protoComponent().cliUcdGetOptsUsage(ident+' ')
            if len(string.strip(s)):
                u = u + '\n' + ident + s
        return u
        
    def cliUcdSetArgs(self, argv):
        if hasattr(self.protoComponent, 'cliUcdSetArgs'):
            while 1:
                val = self.protoComponent()
                newArgv = val.cliUcdSetArgs(argv)
                if len(newArgv) != len(argv):
                    self.append(val)
                    argv = newArgv
                else:
                    argv = newArgv
                    break
        return argv

class ChoiceMixIn:
    cliUcdOptBraces = ('', '')
    def cliUcdGetUsage(self):
        u = ''
        for comp in self.choiceComponents:
            if hasattr(comp, 'cliUcdGetUsage'):
                s = comp().cliUcdGetUsage()
                if s:
                    if len(u):
                        u = u + ' | '
                    u = u + s
        return self.cliUcdOptBraces[0] + u + self.cliUcdOptBraces[1]

    def cliUcdGetOptsUsage(self, ident=''):
        u = ident+'%s initialization:' % self.__class__.__name__
        for comp in self.choiceComponents:
            if hasattr(comp, 'cliUcdGetUsage'):
                s = comp().cliUcdGetOptsUsage(ident+' ')
                if len(string.strip(s)):
                    u = u + '\n' + ident + s
        return u
    
    def cliUcdSetArgs(self, argv):
        for comp in self.choiceComponents:
            if hasattr(comp, 'cliUcdSetArgs'):
                val = comp()
                newArgv = val.cliUcdSetArgs(argv)
                if len(newArgv) != len(argv):
                    self[self.choiceNames[self.choiceComponents.index(comp)]] = val
                    argv = newArgv
                    break
        return argv

class ObjectNameMixIn(OptsParser):
    cliUcdOptId = ''
    cliUcdOptValName = 'OID'
    cliUcdOptBraces = ('<', '>')
    
    def cliUcdOptFilter(self, oid):
        if oid[:1] != '.':
            return '.1.3.6.1.2.1.' + oid
        else:
            return oid            

def mixIn():
    """Register this module's mix-in classes at their bases
    """
    mixInComps = [ (rfc1155.Integer, IntegerMixIn),
                   (rfc1155.OctetString, OctetStringMixIn),
                   (rfc1155.Null, NullMixIn),
                   (rfc1155.ObjectIdentifier, ObjectIdentifierMixIn),
                   (rfc1155.IpAddress, IpAddressMixIn),
                   (rfc1155.Counter, CounterMixIn),
                   (rfc1155.Gauge, GaugeMixIn),
                   (rfc1155.TimeTicks, TimeTicksMixIn),
                   (rfc1155.Sequence, SequenceMixIn),
                   (rfc1155.SequenceOf, SequenceOfMixIn),
                   (rfc1155.Choice, ChoiceMixIn),
                   (rfc1155.ObjectName, ObjectNameMixIn) ]

    for (baseClass, mixIn) in mixInComps:
        if mixIn not in baseClass.__bases__:
            baseClass.__bases__ = (mixIn, ) + baseClass.__bases__
