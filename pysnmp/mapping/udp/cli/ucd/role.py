"""
   UCD-SNMP-style command line interface to role.* objects

   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
from socket import gethostbyname
from string import atoi, split, lower
from pysnmp.error import PySnmpError
from pysnmp.mapping.udp import role
from pysnmp.mapping.udp.cli import error

class ManagerMixIn:
    def cliUcdGetUsage(self):
        return '[ -r <retries> ] [ -t <timeout> ] [ -py <c> ] [ -d ] <[transport:]address>'

    def cliUcdGetOptsUsage(self, ident=''):
        return ident + \
               'transport      run protocol over this transport [udp]\n' + \
               ident + \
               'address        destination agent address (<hostname[:port]> for UDP)\n' + \
               ident + \
               '-r <retries>   set the number of retries [%d]\n' % \
               self.retries +\
               ident + \
               '-t <timeout>   set the request timeout [%d secs]\n' % \
               self.timeout + \
               ident + \
               '-py <c>        match up dest/response addresses [%s]\n' % \
               self.checkPeerAddrFlag + \
               ident + \
               '-d             dump sent & received SNMP packets [%s]\n' % \
               self.dumpPacketsFlag

    def cliUcdSetArgs(self, argv):
        idx = 0; newArgv = []
        while idx < len(argv):
            if argv[idx] == '-r':
                try:
                    self.retries = atoi(argv[idx+1])
                except (IndexError, ValueError), why:
                    raise error.BadArgumentError('Bad or missing value to %s'\
                                                 % argv[idx])
                idx = idx + 2
                continue
            if argv[idx] == '-t':
                try:
                    self.timeout = atoi(argv[idx+1])
                except (IndexError, ValueError), why:
                    raise error.BadArgumentError('Bad or missing value to %s'\
                                                 % argv[idx])
                idx = idx + 2
                continue
            if argv[idx] == '-py' and argv[idx+1] == 'c':
                self.checkPeerAddrFlag = 1
                idx = idx + 2
                continue
            if argv[idx] == '-d':
                self.dumpPacketsFlag = 1
                idx = idx + 1
                continue
            newArgv.append(argv[idx])
            idx = idx + 1
        if not len(newArgv) or not len(newArgv[0]):
            raise error.BadArgumentError('Missing agent name')
        if newArgv[0][0] == '-':
            raise error.BadArgumentError('Unresolved options before agent name (check opts order): %s' % newArgv)
        address = split(newArgv[0], ':')
        if len(address) == 3:
            domain, host, port = apply(lambda x='udp', \
                                       y=None, z='161': (x, y, z), address)
            if lower(domain) != 'udp':
                raise error.BadArgumentError('Unsupported transport domain \'%s\''\
                                             % domain)
        elif 0 < len(address) < 3:
            host, port = apply(lambda x='udp', y='161': (x, y), address)
        else:
            raise error.BadArgumentError('Bad transport spec at \'%s\'' \
                                         % newArgv[idx:])
        try:
            port = atoi(port)
        except ValueError, why:
            raise error.BadArgumentError('Bad port spec at %s: %s' %
                                         (newArgv[idx:], why))
        try:
            host = gethostbyname(host)
        except socket.error, why:
            raise error.BadArgumentError('gethostbyname() failed: %s' % why)
        self.agent = (host, port)
        return newArgv[1:]

class AgentMixIn: pass

def mixIn():
    """Register this module's mix-in classes at their bases
    """
    mixInComps = [ (role.Manager, ManagerMixIn),
                   (role.Agent, AgentMixIn) ]

    for (baseClass, mixIn) in mixInComps:
        if mixIn not in baseClass.__bases__:
            baseClass.__bases__ = (mixIn, ) + baseClass.__bases__
