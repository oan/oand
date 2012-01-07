#!/usr/bin/env python
'''
Serialize an object to a JSON.

Example:
c1 = Test("c1", "file 1")

txt = OANSerializer.encode(c1)
obj = OANSerializer.decode(txt)

self.assertEqual(obj.name, "c1")
self.assertEqual(obj.content, "file 1")

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from json import JSONEncoder, JSONDecoder

# Classes that should be possible to encode and decode.
#from resources import Resource, Folder, File
#from heartbeat import HeartBeat
_cls_list = {}

def add(name, cls):
    _cls_list[name] = cls

def encode(obj):
    return JSONEncoder(default = _encode_hook).encode(obj)

def decode(obj):
    return JSONDecoder(object_hook = _decode_hook).decode(obj)

def _encode_hook(obj):
    if obj.__class__.__name__ not in _cls_list:
        if not isinstance(obj, _cls_list[obj.__class__.__name__]):
            raise TypeError("%r is not JSON serializable" % (obj))

    setattr(obj, 'class_name',  obj.__class__.__name__)
    return obj.__dict__

def _decode_hook(value):
    obj = _cls_list[value['class_name']]()
    for key, val in value.iteritems():
        setattr(obj, key, val)

    return obj
