"""
   UCD-SNMP-style command line interface to SNMP v.2c message PDUs (RFC1905)

   Copyright 1999-2003 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'GetRequestPduMixIn', 'GetNextRequestPduMixIn',
            'SetRequestPduMixIn', 'GetBulkRequestPduMixIn',
            'InformRequestPduMixIn', 'ReportPduMixIn', 'SnmpV2TrapPduMixIn',
            'registerMixIns' ]

from pysnmp.proto import rfc1902, rfc1905
from pysnmp.proto.cli.ucd import rfc1157
from pysnmp.proto.cli import error

# Usage message
parseUcdStyleVarsUsage = rfc1157.parseUcdStyleVarsUsage + \
                         'Types (v.2c):\n' + \
                         '   u:            Unsigned32\n' + \
                         '   c32:          Counter32\n' + \
                         '   g32:          Gauge32\n' + \
                         '   U:            Counter64'

def parseUcdStyleVars(mod, args):
    """Parse UCD-style variables binding command line specification
       into a list of ASN.1 objects
    """
    idx = 0; vars = []
    while idx < len(args):
        try:
            vars.extend(rfc1157.parseUcdStyleVars(mod, args[idx:idx+3]))

        except error.BadArgumentError, why:
            try:
                if args[idx+1] == 'u':
                    vars.append((args[idx], mod.Unsigned32(long(args[idx+2]))))
                elif args[idx+1] == 'c32':
                    vars.append((args[idx], mod.Counter32(long(args[idx+2]))))
                elif args[idx+1] == 'g32':
                    vars.append((args[idx], mod.Gauge32(long(args[idx+2]))))
                elif args[idx+1] in [ 'U', 'c64' ]:
                    vars.append((args[idx], mod.Counter64(long(args[idx+2]))))
                else:
                    raise error.BadArgumentError(why)

            except IndexError:
                raise error.BadArgumentError('Wrong number of arguments supplied')

            except (TypeError, ValueError, SyntaxError), why:
                raise error.BadArgumentError('Wrong type of value \'%s\': %s' % (args[idx+2], why))

        idx = idx + 3

    return vars

class ReadReqPduMixIn(rfc1157.ReadReqPduMixIn): pass

class WriteReqPduMixIn(rfc1157.WriteReqPduMixIn):
    """Write request-specific CLI mix-in class
    """
    def cliUcdGetUsage(self): return parseUcdStyleVarsUsage
    cliGetUsage = cliUcdGetUsage
	
    def cliUcdSetArgs(self, args):
        """Parse C/L args into message components
        """
        if len(args) < 1:
            raise error.BadArgumentError('Missing Object Name')

        self.apiGenSetVarBind(map(lambda x: (rfc1157.makeAbsoluteOid(x[0]), x[1]), parseUcdStyleVars(rfc1902, args)))
        return []
    cliSetArgs = cliUcdSetArgs

class SnmpV2TrapPduMixIn(WriteReqPduMixIn):
    """Trap request-specific CLI mix-in class
    """
    def cliUcdGetUsage(self):
        return '[<trap-parameters>] [<oid type val> ...]]\n' + \
               'Trap parameters (v.2c):\n' + \
               '   [uptime [trap-oid]] ' + \
               parseUcdStyleVarsUsage
    cliGetUsage = cliUcdGetUsage

    def cliUcdSetArgs(self, args):
        """Parse C/L args into message components
        """
        if len(args) > 0 and args[0]:
            try:
                uptime = int(args[0])
                
            except (TypeError, ValueError), why:
                raise error.BadArgumentError('Wrong type of value \'%s\': %s' % (args[0], why))
        else:
            from time import time
            uptime = int(time())

        # TrapOID
        if len(args) > 1 and args[1]:
            trapoid = args[1]
        else:
            trapoid = '1.3.6.1.4.1.3.1.1'

        # First add mandatory variable bindings (see RFC1905)
        self.apiGenSetVarBind( \
            map(lambda x, y: (x, y),
                [ '.1.3.6.1.2.1.1.3.0',
                  '.1.3.6.1.6.3.1.1.4.1.0' ],
                [ rfc1902.TimeTicks(uptime),
                  rfc1902.ObjectIdentifier(trapoid)])
            + map(lambda x: (v1.makeAbsoluteOid(x[0]), x[1]),
                  parseUcdStyleVars(rfc1902, args[2:])))

        return []
    cliSetArgs = cliUcdSetArgs

# Alias to v.1-style name
TrapPduMixIn = SnmpV2TrapPduMixIn

class GetRequestPduMixIn(ReadReqPduMixIn): pass
class GetNextRequestPduMixIn(ReadReqPduMixIn): pass
class SetRequestPduMixIn(WriteReqPduMixIn): pass
class GetBulkRequestPduMixIn(ReadReqPduMixIn): pass
class InformRequestPduMixIn(ReadReqPduMixIn): pass
class ReportPduMixIn(ReadReqPduMixIn): pass

def mixIn():
    """Register this module's mix-in classes at their bases
    """
    mixInComps = [ (rfc1905.GetRequestPdu, GetRequestPduMixIn),
                   (rfc1905.GetNextRequestPdu, GetNextRequestPduMixIn),
                   (rfc1905.SetRequestPdu, SetRequestPduMixIn),
                   (rfc1905.GetBulkRequestPdu, GetBulkRequestPduMixIn),
                   (rfc1905.InformRequestPdu, InformRequestPduMixIn),
                   (rfc1905.ReportPdu, ReportPduMixIn),
                   (rfc1905.SnmpV2TrapPdu, SnmpV2TrapPduMixIn) ]

    for (baseClass, mixIn) in mixInComps:
        if mixIn not in baseClass.__bases__:
            baseClass.__bases__ = baseClass.__bases__ + (mixIn, )
