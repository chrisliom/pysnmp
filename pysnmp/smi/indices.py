"""Ordered dictionaries classes used for indices"""
from types import DictType
from string import join, split, atol

try:
    from sys import version_info
except ImportError:
    version_info = ( 0, 0 )   # a really early version

if version_info < (2, 2):
    class OrderedDict:
        def __init__(self, **kwargs):
            self.__dict = {}
            self.__keys = []
            self.__dirty = 0
            self.__sortingFun = cmp
            if kwargs:
                self.update(kwargs)
                self.__dirty = 1
        def __getitem__(self, key): return self.__dict[key]
        def __setitem__(self, key, value):
            if not self.__dict.has_key(key):
                self.__keys.append(key)
            self.__dict[key] = value
            self.__dirty = 1
        def __repr__(self):
            if self.__dirty: self.__order()
            return repr(self.__dict)
        def __str__(self):
            if self.__dirty: self.__order()
            return str(self.__dict)
        def __delitem__(self, key):
            if self.__dict.has_key(key):
                self.__keys.remove(key)
            del self.__dict[key]
            self.__dirty = 1
        __delattr__ = __delitem__
        def clear(self):
            self.__dict.clear()
            self.__keys = []
            self.__dirty = 1
        def get(self, key, default=None): return self.__dict.get(key, default)
        def has_key(self, key): return self.__dict.has_key(key)
        def keys(self):
            if self.__dirty: self.__order()
            return list(self.__keys)
        def values(self):
            if self.__dirty: self.__order()
            return map(lambda k, d=self.__dict: d[k], self.__keys)
        def items(self):
            if self.__dirty: self.__order()
            return map(lambda k, d=self.__dict: (k, d[k]), self.__keys)
        def update(self, d):
            map(lambda (k, v), self=self: self.__setitem__(k, v), d.items())
        def __order(self):
            if self.__sortingFun:
                self.__keys.sort(self.__sortingFun)
            self.__dirty = 0
        def setSortingFun(self, fun):
            self.__sortingFun = fun
            self.__dirty = 1            
else:
    class OrderedDict(DictType):
        def __init__(self, **kwargs):
            self.__keys = []
            self.__dirty = 0
            self.__sortingFun = cmp
            super(OrderedDict, self).__init__()
            if kwargs:
                self.update(kwargs)
        def __setitem__(self, key, value):
            if not self.has_key(key):
                self.__keys.append(key)
            super(OrderedDict, self).__setitem__(key, value)
            self.__dirty = 1
        def __repr__(self):
            if self.__dirty: self.__order()
            return super(OrderedDict, self).__repr__()
        def __str__(self):
            if self.__dirty: self.__order()
            return super(OrderedDict, self).__str__()
        def __delitem__(self, key):
            if super(OrderedDict, self).has_key(key):
                self.__keys.remove(key)
            super(OrderedDict, self).__delitem__(key)
            self.__dirty = 1            
        __delattr__ = __delitem__
        def clear(self):
            super(OrderedDict, self).clear()
            self.__keys = []
            self.__dirty = 1        
        def keys(self):
            if self.__dirty: self.__order()
            return list(self.__keys)
        def values(self):
            if self.__dirty: self.__order()
            return map(lambda k, d=self: d[k], self.__keys)
        def items(self):
            if self.__dirty: self.__order()
            return map(lambda k, d=self: (k, d[k]), self.__keys)
        def update(self, d):
            map(lambda (k, v), self=self: self.__setitem__(k, v), d.items())
        def __order(self):
            if self.__sortingFun:
                self.__keys.sort(self.__sortingFun)
            self.__dirty = 0
        def setSortingFun(self, fun):
            self.__sortingFun = fun
            self.__dirty = 1

class OidOrderedDict(OrderedDict):
    def __init__(self, **kwargs):
        self.__keysCache = {}
        apply(OrderedDict.__init__, [self], kwargs)        
        self.setSortingFun(lambda o1, o2, self=self: cmp(
            self.__keysCache[o1], self.__keysCache[o2]))

    def __setitem__(self, key, value):
        if not self.__keysCache.has_key(key):
            self.__keysCache[key] = map(
                lambda x: atol(x), filter(None, split(key, '.'))
                )
        OrderedDict.__setitem__(self, key, value)

        def __delitem__(self, key):
            if self.__keysCache.has_key(key):
                del self.__keysCache[key]
            OrderedDict.__delitem__(self, key)
        __delattr__ = __delitem__

