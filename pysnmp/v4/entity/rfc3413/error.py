from pysnmp.error import PySnmpError

class ApplicationReturn(PySnmpError):
    def __init__(self, **kwargs):
        self.__errorIndication = kwargs
    def __str__(self): return str(self.__errorIndication)
    def __getitem__(self, key): return self.__errorIndication[key]
    def has_key(self, key): return self.__errorIndication.has_key(key)
    def get(self, key, defVal=None):
        return self.__errorIndication.get(key, defVal)
