"""RFC1903 SMI macros implementations"""
from string import join, split, digits, atoi
from pysnmp.asn1.univ import Integer, OctetString
from pysnmp.smi.node import MibType
from pysnmp.smi import error

class TextualConvention(MibType):
    def strSmiEntry(self):
        r = [ '%s TEXTUAL-CONVENTION' % self.get('name') ]
        if self.get('displayHint'):
            r.append('DISPLAY-HINT \"%s\"' % self.get('displayHint'))
        if self.get('status'):
            r.append('STATUS \"%s\"' % self.get('status'))
        if self.get('description'):
            r.append('DESCRIPTION \"%s\"' % self.get('description'))
        if self.get('reference'):
            r.append('REFERENCE \"%s\"' % self.get('reference'))
        if self.get('baseName'):
            # XXX format constraints
            r.append('SYNTAX %s' % self.get('baseName'))
        return join(r, '\n')
        
    def outputFilter(self, mibTree, value):
        """Implements DISPLAY-HINT evaluation"""
        syntax = self.getSyntax(mibTree)
        displayHint = self.get('displayHint')
        if not displayHint:
            return MibType.outputFilter(self, mibTree, value)
        if isinstance(syntax, Integer):
            t, f = apply(lambda t, f=0: (t, f), split(displayHint, '-'))
            if t == 'x':
                return '0x%x' % value
            elif t == 'd':
                try:
                    return '%.*f' % (int(f), float(value)/pow(10, int(f)))
                except StandardError, why:
                    raise error.BadArgumentError(
                        'float num evaluation error at %r: %s' % (self, why)
                    )
            elif t == 'o':
                return '0%o' % value
            elif t == 'b':
                v = value; r = ['B']
                while v:
                    r.insert(0, '%d' % (v&0x01))
                    v = v>>1
                return join(r, '')
            else:
                raise error.BadArgumentError(
                    'Unsupported numeric type spec at %r: %s' % (self, t)
                    )
            
        elif isinstance(syntax, OctetString):
            r = ''
            if isinstance(value, OctetString):
                v = value.get()
            else:
                v = value
            d = displayHint
            while v and d:
                # 1
                if d[0] == '*':
                    repeatIndicator = repeatCount = int(v[0])
                    d = d[1:]; v = v[1:]
                else:
                    repeatCount = 1; repeatIndicator = None
                    
                # 2
                octetLength = ''
                while d and d[0] in digits:
                    octetLength = octetLength + d[0]
                    d = d[1:]
                try:
                    octetLength = int(octetLength)
                except StandardError, why:
                    raise error.BadArgumentError(
                        'Bad octet length at %r: %s' % (self, octetLength)
                        )                    
                if not d:
                    raise error.BadArgumentError(
                        'Short octet length at %r: %s' % (self, displayHint)
                        )
                # 3
                displayFormat = d[0]
                d = d[1:]

                # 4
                if d and d[0] not in digits and d[0] != '*':
                    displaySep = d[0]
                    d = d[1:]
                else:
                    displaySep = ''

                # 5
                if d and displaySep and repeatIndicator is not None:
                        repeatTerminator = d[0]
                        displaySep = ''
                        d = d[1:]
                else:
                    repeatTerminator = None

                while repeatCount:
                    repeatCount = repeatCount - 1
                    if displayFormat == 'a':
                        r = r + v[:octetLength]
                    elif displayFormat in ('x', 'd', 'o'):
                        n = 0L; vv = v[:octetLength]
                        while vv:
                            n = n << 8
                            try:
                                n = n | ord(vv)
                                vv = vv[1:]
                            except StandardError, why:
                                raise error.BadArgumentError(
                                    'Display format eval failure for %r at %r: %s'
                                    % (vv, self, why)
                                    )
                        if displayFormat == 'x':
                            r = r + '%02x' % n
                        elif displayFormat == 'o':
                            r = r + '%03o' % n
                        else:
                            r = r + '%d' % n
                    else:
                        raise error.BadArgumentError(
                            'Unsupported display format char at %r: %s' %
                            (self, displayFormat)
                            )
                    if v and repeatTerminator:
                        r = r + repeatTerminator
                    v = v[octetLength:]
                if v and displaySep:
                    r = r + displaySep
                if not d:
                    d = displayHint
#             if d:
#                 raise error.BadArgumentError(
#                     'Unparsed display hint left at %r: %s' % (self, d)
#                     )                    
            return r
        else:
            return str(syntax.set(value))

if __name__ == '__main__':
#    tc = TextualConvention(syntax=Integer(), displayHint='x')
#    print tc.outputFilter(Integer(1234))
    tc = TextualConvention(syntax=OctetString('\x00\x06SEK\xe0'), displayHint='1x')
    print tc.outputFilter(OctetString('123456'))
