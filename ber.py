#
# Basic Encoding Rules (BER) for ASN.1 data types
#
# Written by Ilya Etingof <ilya@glas.net>, 1999
#
# This code is partially derived from Simon Leinen's <simon@switch.ch>
# BER PERL module.
#

# import modules
import string
import objid

# module specific exceptions
unknown_tag='Unknown packet tag'
bad_encoding='Incorrect BER encoding'
bad_subjid='Bad sub-object ID'
bad_ipaddr='Bad IP address'
type_error='ASN.1 data types mismatched'
bad_argument='Bad argument'

# flags for BER tags
FLAGS = { 
    'UNIVERSAL': 0x00,
    'APPLICATION' : 0x40,
    'CONTEXT' : 0x80,
    'PRIVATE' : 0xC0,
    # extended tags
    'PRIMITIVE': 0x00,
    'CONSTRUCTOR' : 0x20
}

# universal BER tags
TAGS = {
    'BOOLEAN' : 0x00,
    'INTEGER' : 0x02,
    'BITSTRING' : 0x03,
    'OCTETSTRING' : 0x04,
    'NULL' : 0x05,
    'OBJID' : 0x06,
    'SEQUENCE' : 0x10,
    'SET' : 0x11,
    'UPTIME' : 0x43,
# SNMP specific tags
    'IPADDRESS' : 0x00 | FLAGS['APPLICATION'],
    'COUNTER32' : 0x01 | FLAGS['APPLICATION'],
    'GAUGE32' : 0x02 | FLAGS['APPLICATION'],
    'TIMETICKS' : 0x03 | FLAGS['APPLICATION'],
    'OPAQUE' : 0x04 | FLAGS['APPLICATION'],
    'NSAPADDRESS' : 0x05 | FLAGS['APPLICATION'],
    'COUNTER64' : 0x06 | FLAGS['APPLICATION'],
    'UNSIGNED32' : 0x07 | FLAGS['APPLICATION'],
    'TAGGEDSEQUENCE' : 0x10 | FLAGS['CONSTRUCTOR'],
# SNMP PDU specifics
    'GETREQUEST' : 0x00 | FLAGS['CONTEXT'] | FLAGS['CONSTRUCTOR'],
    'GETNEXTREQUEST' : 0x01 | FLAGS['CONTEXT'] | FLAGS['CONSTRUCTOR'],
    'GETRESPONSE' : 0x02 | FLAGS['CONTEXT'] | FLAGS['CONSTRUCTOR'],
    'SETREQUEST' : 0x03 | FLAGS['CONTEXT'] | FLAGS['CONSTRUCTOR'],
    'TRAPREQUEST' : 0x04 | FLAGS['CONTEXT'] | FLAGS['CONSTRUCTOR']
}

# BER encoders / decoders
class ber (objid.objid):
    #
    # BER HEADER ENCODERS / DECODERS
    #

    # encode a tag
    def encode_tag (self, name=None):
        """encode ASN.1 data type tag"""
        # check the argument
        if not name:
            raise bad_argument

        # lookup the tag ID by name
        if TAGS.has_key(name):
            return '%c' % TAGS[name]
        raise unknown_tag

    # encode length
    def encode_length (self, length=None):
        """encode BER length"""
        # check the argument
        if length == None:
            raise bad_argument

        # if given length fits one byte
        if length < 0x80:
            return '%c' % length
        # two bytes required
        elif length < 0xFF:
            return '%c%c' % (0x81, length)
        # three bytes required
        else:
            return '%c%c%c' % (0x82, \
                (length >> 8) & 0xFF, \
                length & 0xFF)

    # decode tag
    def decode_tag (self, tag=None):
        """decode ASN.1 data type tag"""
        # check the argument
        if tag == None:
            raise bad_argument

        # lookup the tag in the dictionary of known tags
        for key in TAGS.keys():
            if tag == TAGS[key]:
                return key
        raise unknown_tag

    # decode length
    def decode_length (self, packet=None):
        """encode BER length"""
        # check the argument
        if packet == None:
            raise bad_argument

        # get the most-significant-bit
        msb = ord(packet[0]) & 0x80
        if not msb:
            return (ord(packet[0]) & 0x7F, 1)

        # get the size if the length
        size = ord(packet[0]) & 0x7F

        # one byte length
        if msb and size == 1:
            return (ord(packet[1]), size+1)

        # two bytes length
        elif msb and size == 2:
            result = ord(packet[1])
            result = result << 8
            return (result | ord(packet[2]), size+1)

    #
    # ASN.1 DATA TYPES ENCODERS
    #

    # encode tagged integer
    def encode_an_integer (self, tag, integer=None):
        """encode tagged integer"""
        # check the argument
        if integer == None:
            raise bad_argument

        # initialize result
        result = ''

        # make a local copy
        arg = integer

        # determine the sign
        if arg >= 0:
            sign = 0
        else:
            sign = 0xFF

        # pack the argument
        while 1:
            # pack an octet
            result = '%c' % int(arg & 0xff) + result

            # stop as everything got packed
            if arg >= -128 and arg < 128:
                return self.encode_tag(tag) + \
                    self.encode_length(len(result)) + \
                    result

            # move to the next octet
            arg = arg - sign;
            arg = int(arg / 256)

        # return error
        raise bad_encoding

    # encode integer
    def encode_integer (self, integer):
        """encode ASN.1 integer"""
        return self.encode_an_integer ('INTEGER', integer)

    # encode a sequence
    def encode_a_sequence (self, tag, sequence=None):
        """encode a tagged sequence"""
        # check the argument
        if sequence == None:
            raise bad_argument

        # make a local copy and add a leading empty item
        result = sequence

        # return encoded packet
        return self.encode_tag(tag) + \
            self.encode_length(len(result)) + \
            result

    # encode sequence
    def encode_sequence (self, sequence):
        """encode ASN.1 sequence"""
        return self.encode_a_sequence ('TAGGEDSEQUENCE', sequence)

    # encode SNMP PDU sequence of specified type
    def encode_snmp_pdu_sequence (self, type, sequence):
        """encode SNMP PDU ASN.1 sequence of specified type"""
        return self.encode_a_sequence (type, sequence)

    # encode an octets string
    def encode_string (self, string=None):
        """encode ASN.1 string"""
        # check the argument
        if not string:
            raise bad_argument

        # encode the string
        return self.encode_tag('OCTETSTRING') + \
            self.encode_length(len(string)) + \
            string

    # encode an OBJID
    def encode_oid (self, oids=None):
        """encode ASN.1 object ID"""
        # check the argument
        if not oids:
            raise bad_argument

        # set up index
        index = 0

        # skip leading empty oid
        while not oids[index]:
            index = index + 1

        # build the first twos
        if len(oids[index:]) > 1:
            result = oids[index] * 40
            result = result + oids[index+1]
            result = '%c' % int(result)

        # setup index
        index = index + 2

        # cycle through subids
        while index < len(oids):
            # pick a subid
            subid = oids[index]

            # 7 bits long subid
            if subid >= 0 and subid < 128:
                result = result + '%c' % subid
            # 14 bits long subid
            elif subid >= 128 and subid < 16384:
                result = result + '%c%c' % \
                (0x80 | (subid >> 7), \
                subid & 0x7f)
            # 21 bits long subid
            elif subid >= 16384 and subid < 2097152:
                result = result + '%c%c%c' % \
                (0x80 | ((subid >> 14) & 0x7f), \
                0x80 | (subid >> 7), \
                subid & 0x7f)
            # 28 bits long subid
            elif subid >= 2097152 and subid < 268435456:
                result = result + '%c%c%c%c' % \
                (0x80 | ((subid>>21) & 0x7f), \
                0x80 | ((subid >> 14) & 0x7f), \
                0x80 | (subid >> 7), \
                subid & 0x7f)
            # 31 bits long subid
            elif subid >= 268435456L and subid < 2147483648L:
                result = result + '%c%c%c%c%c' % \
                (0x80 | ((subid>>28) & 0x0f), \
                0x80 | ((subid>>21) & 0x7f), \
                0x80 | ((subid >> 14) & 0x7f), \
                0x80 | (subid >> 7), \
                subid & 0x7f)
            # 32 bits long subid
            elif subid >= -2147483648L and subid < 0:
                result = result + '%c%c%c%c%c' % \
                (0x80 | ((subid>>28) & 0x0f), \
                0x80 | ((subid>>21) & 0x7f), \
                0x80 | ((subid >> 14) & 0x7f), \
                0x80 | (subid >> 7), \
                subid & 0x7f)
            else:
                raise bad_sobjid

            # move to the next subid
            index = index + 1
        return self.encode_tag('OBJID') + \
            self.encode_length(len(result)) + result

    # encode an IP address
    def encode_ipaddr (self, addr):
        """encode ASN.1 IP address"""
        # assume address is given in dotted notation
        packed = string.split(addr, '.')

        # make sure it is four octets length
        if len(packed) != 4:
            raise bad_ipaddr

        # convert string octets into integer counterparts
        # (this is still not immune to octet overflow)
        try:
            packed = map(lambda x: string.atoi (x), packed)
        except string.atoi_error:
            raise bad_ipaddr
	    
        # build a result
        result = '%c%c%c%c' % (packed[0], packed[1],\
                               packed[2], packed[3])

        # return encoded result
        return self.encode_tag('IPADDRESS') + \
            self.encode_length(len(packed)) + \
            result

    # encode timeticks
    def encode_timeticks (self, timeticks):
        """encode ASN.1 timeticks"""
        return self.encode_an_integer ('TIMETICKS', timeticks)

    # encode null
    def encode_null(self):
        """encode ASN.1 NULL"""
        return self.encode_tag('NULL') + self.encode_length(0)

    #
    # ASN.1 DATA TYPES DECODERS
    #

    # decode signed integer (of any length)
    def decode_integer_s (self, packet=None, sign=None):
        """decode signed ASN.1 integer"""
        # check the argument
        if packet == None or sign == None:
            raise bad_argument

        # now unpack the length
        (length, size) = self.decode_length(packet[1:])

        # setup an index on the data area
        index = size+1

        # get the first octet
        result = ord (packet[index])

        # first octet indicates the sign
        if sign and result & 0x80:
            # signed integer
            result = -long(result)
        else:
            # unsigned integer
            result = long(result)

        # concatinate the rest
        while index < length+size:
            index = index + 1
            result = result * 256
            result = result + ord(packet[index])

        # return result
        return result

    # decode an unsigned integer
    def decode_unsigned (self, packet):
        """decode unsigned ASN.1 integer"""
        return self.decode_integer_s (packet, 0)

    # decode a signed integer
    def decode_integer (self, packet):
        """decode signed ASN.1 integer"""
        return self.decode_integer_s (packet, 1)

    # decode a sequence
    def decode_sequence (self, packet=None):
        """decode ASN.1 sequence"""
        # check the argument
        if packet == None:
            raise bad_argument

        # now unpack the length
        (length, size) = self.decode_length(packet[1:])

        # return the sequence
        return packet[size+1:size+length+1]

    # decode a string of octets
    def decode_string (self, packet=None):
        """decode ASN.1 string"""
        # check the argument
        if packet == None:
            raise bad_argument

        # make sure data types matched
        if self.decode_tag(ord(packet[0])) != 'OCTETSTRING':
            raise type_error

        # now unpack the length
        (length, size) = self.decode_length(packet[1:])

        # return the octets string
        return packet[size+1:size+length+1]

    # decode objid
    def decode_oid (self, packet=None):
        """decode ASN.1 object ID"""
        # check the argument
        if packet == None:
            raise bad_argument

        # make sure data types matched
        if self.decode_tag(ord(packet[0])) != 'OBJID':
            raise type_error

        # create a list for objid
        oid = []

        # unpack the length
        (length, size) = self.decode_length(packet[1:])

        # set up index
        index = size+1

        # get the first subid
        subid = ord (packet[index])
        oid.append(int(subid / 40))
        oid.append(int(subid % 40))

        # progress index
        index = index + 1

        # loop through the rest
        while index < length + size + 1:
            # get a subid
            subid = ord (packet[index])

            if subid < 128:
                oid.append(subid)
                index = index + 1
            else:
                # construct subid from a number of octets
                next = subid
                subid = 0
                while next >= 128:
                    # collect subid
                    subid = (subid << 7) + (next & 0x7F)

                    # take next octet
                    index = index + 1
                    next = ord (packet[index])

                    # just for sure
                    if index > length + size:
                        return bad_integer

                # append a subid to oid list
                subid = (subid << 7) + next
                oid.append(subid)
                index = index + 1

        # return objid
        return oid      

    # decode uptime
    def decode_uptime (self, packet=None):
        """decode ASN.1 uptime"""
        # check the argument
        if packet == None:
            raise bad_argument

        # make sure data types matched
        if self.decode_tag(ord(packet[0])) != 'UPTIME':
            raise type_error

        # decode as unsigned integer
        return self.decode_an_unsigned (packet)

    # decode ipaddress
    def decode_ipaddress (self, packet=None):
        """decode ASN.1 IP address"""
        # check the argument
        if packet == None:
            raise bad_argument

        # make sure data types matched
        if self.decode_tag(ord(packet[0])) != 'IPADDRESS':
            raise type_error

        # get the value from the packet
        ipaddr = self.decode_sequence (packet)

        # check it is valid
        if len(ipaddr) != 4:
            raise bad_ipaddr

        # return in dotted notation
        return '%d.%d.%d.%d' % \
            (ord(ipaddr[0]), ord(ipaddr[1]), \
            ord(ipaddr[2]), ord(ipaddr[3]))

    # decode null
    def decode_null(self, packet=None):
        """decode ASN.1 NULL"""
        # check the argument
        if packet == None:
            raise bad_argument

        # make sure data types matched
        if self.decode_tag(ord(packet[0])) != 'NULL':
            raise type_error

        # now unpack the length
        (length, size) = self.decode_length(packet[1:])

        # return nothing
        return ''

    # decode timticks
    def decode_timeticks (self, packet=None):
        """decode ASN.1 timticks"""
        # check the argument
        if packet == None:
            raise bad_argument

        # make sure data types matched
        if self.decode_tag(ord(packet[0])) != 'TIMETICKS':
            raise type_error

        # decode as unsigned integer
        return self.decode_unsigned (packet)

    # decode given encoded value according to its type
    def decode_value (self, packet=None):
        """decode ASN.1 typed value"""
        # check the argument
        if packet == None:
            raise bad_argument

        # get a tag
        tag = self.decode_tag(ord(packet[0]))

        # if it's a string
        if tag == 'OCTETSTRING':
            return self.decode_string(packet)
        elif tag == 'INTEGER':
            return self.decode_integer(packet)
        elif tag == 'UPTIME':
            return self.decode_uptime(packet)
        elif tag == 'IPADDRESS':
            return self.decode_ipaddress(packet)
        elif tag == 'TIMETICKS':
            return self.decode_timeticks(packet)
        elif tag == 'COUNTER32' or \
            tag == 'COUNTER64' or \
                tag == 'GAUGE32':
            return self.decode_unsigned(packet)
        # The following OBJID value processing has been suggested
        # by Case Van Horsen, March 14, 2000
        elif tag == 'OBJID':
            objid_n = self.decode_oid(packet)
            return self.nums2str(objid_n)
        else:
            return 'Unprintable value: ' + tag

    # compare OID'es, return non-zero if OID1 is a prefix of OID2
    def oid_prefix_check (self, enc_oid_1, enc_oid_2):
        """Compare OID'es, return non-zero if OID1 is a prefix of
           OID2. This can be used in the termination condition of
           a loop that walks a table using GetNext or GetBulk"""

        # decode both objid's
        oid_1 = self.decode_oid(enc_oid_1)
        oid_2 = self.decode_oid(enc_oid_2)

        # pick the shortest oid
        if len(oid_1) <= len(oid_2):
            # get the length
            length = len(oid_1)

            # compare oid'es
            if oid_1[:length] == oid_2[:length]:
                return 1
        return 0
