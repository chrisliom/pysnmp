# Extract SNMP version from serialized message
from pysnmp.asn1 import univ

__all__ = [ 'SnmpMsgDemuxer' ]

class SnmpMsgDemuxer(univ.Sequence):
    class RestOfStream(univ.OctetString):
        def decodeItem(self, octetStream, codecId=None):
            self.set(octetStream)
            return ''
    protoComponents = {
        'version': univ.Integer(),
        'rest_of_stream': RestOfStream()
        }
    protoSequence = ( 'version', 'rest_of_stream' )

# XXX Do we really nead protoComponents? maybe ordered dict would help?
