"""
   UCD-SNMP-style command line interface to SNMP v.1 message PDUs (RFC1157)

   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'GetRequestPduMixIn', 'GetNextRequestPduMixIn',
            'SetRequestPduMixIn', 'TrapPduMixIn', 'registerMixIns' ]

from string import atoi, split
from pysnmp.proto import rfc1155, rfc1157
from pysnmp.proto.cli import error

def makeAbsoluteOid(oid):
    """Expand relative OID by prefixing it with the
       iso.org.dod.internet.mgmt.mib OID
    """
    if len(oid) and oid[0] != '.':
        return '.1.3.6.1.2.1.' + oid
    else:
        return oid

# Usage message
parseUcdStyleVarsUsage = '<oid type val [...]>\n' + \
                         'Types (v.1):\n' + \
                         '   i:            INTEGER\n' + \
                         '   s:            STRING\n' + \
                         '   x:            HEX STRING\n' + \
                         '   d:            DECIMAL STRING\n' + \
                         '   n:            NULL OBJECT\n' + \
                         '   o:            OBJECT IDENTIFIER\n' + \
                         '   t:            TimeTicks\n' + \
                         '   a:            IpAddress\n' + \
                         '   c:            Counter\n' + \
                         '   g:            Gauge\n' + \
                         '   p:            Opaque\n'

def parseUcdStyleVars(mod, args):
    """Parse UCD-style variables binding command line specification
       into a list of ASN.1 objects
    """
    idx = 0; vars = []
    while idx < len(args):
        try:
            if args[idx+1] == 'i':
                val = mod.Integer(long(args[idx+2]))
            elif args[idx+1] == 's':
                val = mod.OctetString(args[idx+2])
            elif args[idx+1] == 'x':
                val = args[idx+2]
                if val[:2] == '0x' or val[:2] == '0X':
                    val = val[2:]
                if len(val) % 2:
                    raise error.BadArgumentError('Odd HEX value: %s'\
                                                 % args[idx+2])
                val = reduce(lambda x, y: x+y, map(lambda x: '%c' % eval('0x' + x), map(lambda idx, x=val: x[idx:idx+2], range(0, len(val), 2))))
                val = mod.OctetString(val)
            elif args[idx+1] == 'd':
                val = args[idx+2]
                val = split(val, '.')
                if len(val) != 2:
                    raise error.BadArgumentError('Bad decimal point in value: %s' % args[idx+2])
                val = map(lambda x: atoi(x), val)
                if reduce(lambda x, y: x+y, filter(lambda x: x > 255, val), 0):
                    raise error.BadArgumentError('Decimal component overflow in value: %s' % args[idx+2])
                val = reduce(lambda x, y: x+y, map(lambda x: '%c' % x, val))
                val = mod.OctetString(val)
            elif args[idx+1] == 'n':
                    val = mod.Null(args[idx+2])
            elif args[idx+1] == 'o':
                val = mod.ObjectIdentifier(args[idx+2])
            elif args[idx+1] == 't':
                val = mod.TimeTicks(long(args[idx+2]))
            elif args[idx+1] == 'a':
                val = mod.NetworkAddress(internet=mod.IpAddress(args[idx+2]))
            elif args[idx+1] == 'g':
                val = mod.Gauge(long(args[idx+2]))
            elif args[idx+1] == 'p':
                val = mod.Opaque(args[idx+2])
            elif args[idx+1] == '=':
                raise error.NotImplementedError('MIB lookup not yet implemented')
            else:
                raise error.BadArgumentError('Unknown value type \'%s\'' % (args[idx+1]))

            vars.append((args[idx], val))

            idx = idx + 3
            
        except IndexError:
            raise error.BadArgumentError('Wrong number of arguments supplied')

        except (TypeError, ValueError, SyntaxError), why:
            raise error.BadArgumentError('Wrong type of value \'%s\': %s' % (args[idx+2], why))

    return vars

class ReadReqPduMixIn:
    """Read request-PDU specific CLI mix-in class
    """
    def cliUcdGetUsage(self): return '<obj-id [[obj-id] ... ]'
    def cliUcdSetArgs(self, args):
        """Parse C/L args into message PDU components
        """
        if len(args) < 1:
            raise error.BadArgumentError('Missing Object Name')

        self.apiGenSetVarBind(map(lambda x: (makeAbsoluteOid(x), None), args))
        return []
    cliSetArgs = cliUcdSetArgs

class WriteReqPduMixIn:
    """Write request-PDU specific CLI mix-in class
    """
    def cliUcdGetUsage(self): return parseUcdStyleVarsUsage
    def cliUcdSetArgs(self, args):
        """Parse C/L args into message components
        """
        if len(args) < 1:
            raise error.BadArgumentError('Missing Object Name')

        self.apiGenSetVarBind(map(lambda x: (makeAbsoluteOid(x[0]), x[1]), parseUcdStyleVars(rfc1155, args)))
        return []
    cliSetArgs = cliUcdSetArgs

class TrapPduMixIn(WriteReqPduMixIn):
    """Trap request-specific CLI mix-in class
    """
    def cliUcdGetUsage(self):
        return '[trap-parameters [variables]]\n' + \
               'Trap parameters (v.1):\n' + \
               '   [enterprise-oid [agent [trap-type [specific-type [uptime]]]]]] ' + parseUcdStyleVarsUsage
    cliGetUsage = cliUcdGetUsage

    def cliUcdSetArgs(self, args):
        """Parse C/L args into message PDU components
        """
        if len(args) > 0 and args[0]:
            self.apiGenSetEnterprise(args[0])
        if len(args) > 1 and args[1]:
            self.apiGenSetAgentAddr(args[1])
        else:
            import socket
            self.apiGenSetAgentAddr(socket.gethostbyname(socket.gethostname()))
        if len(args) > 2 and args[2]:
            try:
                self.apiSetGenericTrap(int(args[2]))
            except (TypeError, ValueError), why:
                raise error.BadArgumentError('Wrong type of value \'%s\': %s' % (args[2], why))
        if len(args) > 3 and args[3]:
            try:
                self.apiGenSetSpecificTrap(int(args[3]))
            except (TypeError, ValueError), why:
                raise error.BadArgumentError('Wrong type of value \'%s\': %s' % (args[3], why))
        if len(args) > 4 and args[4]:
            try:
                self.apiGenSetTimeStamp(int(args[4]))
            except (TypeError, ValueError), why:
                raise error.BadArgumentError('Wrong type of value \'%s\': %s' % (args[4], why))

        self.apiGenSetVarBind(map(lambda x: (makeAbsoluteOid(x[0]), x[1]), parseUcdStyleVars(rfc1155, args[5:])))
        return []
    cliSetArgs = cliUcdSetArgs

class GetRequestPduMixIn(ReadReqPduMixIn): pass
class GetNextRequestPduMixIn(ReadReqPduMixIn): pass
class SetRequestPduMixIn(WriteReqPduMixIn): pass
class TrapPduMixIn(TrapPduMixIn): pass

def mixIn():
    """Register this module's mix-in classes at their bases
    """
    mixInComps = [ (rfc1157.GetRequestPdu, GetRequestPduMixIn),
                   (rfc1157.GetNextRequestPdu, GetNextRequestPduMixIn),
                   (rfc1157.SetRequestPdu, SetRequestPduMixIn),
                   (rfc1157.TrapPdu, TrapPduMixIn) ]

    for (baseClass, mixIn) in mixInComps:
        if mixIn not in baseClass.__bases__:
            baseClass.__bases__ = baseClass.__bases__ + (mixIn, )
