"""RFC1902 SMI macros implementations"""
from string import join
from pysnmp.smi.node import MibNode

class ModuleIdentity(MibNode):
    def strSmiEntry(self):
        r = [ '%s MODULE-IDENTITY' % self.get('label') ]
        if self.get('lastUpdated'):
            r.append('LAST-UPDATED \"%s\"' % self.get('lastUpdated'))
        if self.get('organization'):
            r.append('ORGANIZATION \"%s\"' % self.get('organization'))
        if self.get('contactInfo'):
            r.append('CONTACT-INFO \"%s\"' % self.get('contactInfo'))
        if self.get('description'):
            r.append('DESCRIPTION \"%s\"' % self.get('description'))
        if self.get('revisions'):
            for date, descr in self.get('revisions'):
                r.append('REVISION \"%s\"' % date)
                r.append('DESCRIPTION \"%s\"' % descr)
        if self.get('value'):
            r.append(' = { %s }' % self.get('value'))
        return join(r, '\n')

class ObjectIdentity(MibNode): pass

class ObjectType(MibNode):
    def strSmiEntry(self):
        r = [ '%s OBJECT-TYPE' % self.get('name') ]
        if self.get('syntax') is not None:
            r.append('SYNTAX %s' % self.get('syntax').__class__.__name__)
        if self.get('units'):
            r.append('UNITS \"%s\"' % self.get('units'))
        if self.get('maxAccess'):
            r.append('MAX-ACCESS \"%s\"' % self.get('maxAccess'))
        if self.get('status'):
            r.append('STATUS \"%s\"' % self.get('status'))
        if self.get('description'):
            r.append('DESCRIPTION \"%s\"' % self.get('description'))
        if self.get('reference'):
            r.append('REFERENCE \"%s\"' % self.get('reference'))
        if self.get('index'):
            r.append('INDEX { %s }' % join(self.get('index'), ', '))
        if self.get('augments'):
            r.append('AUGMENTS { %s }' % join(self.get('augments'), ', '))
        if self.get('defVal'):
            r.append('DEFVAL { %s }' % join(self.get('defVal'), ', '))
        if self.get('value'):
            r.append(' = { %s }' % self.get('value'))
        return join(r, '\n')
    
class NotificationType(MibNode):
    def strSmiEntry(self):
        r = [ '%s NOTIFICATION-TYPE' % self.get('name') ]
        if self.get('status'):
            r.append('STATUS \"%s\"' % self.get('status'))
        if self.get('description'):
            r.append('DESCRIPTION \"%s\"' % self.get('description'))
        if self.get('reference'):
            r.append('REFERENCE \"%s\"' % self.get('reference'))
        if self.get('objects'):
            r.append('OBJECTS { %s }' % join(self.get('objects'), ', '))
        if self.get('value'):
            r.append(' = { %s }' % self.get('value'))
        return join(r, '\n')
