#!/usr/bin/env python
"""
Serialize/unserialize an object to and from a JSON.

Example:
c1 = Test("c1", "file 1")

serializer.add("Test", Test)
txt = serializer.encode(c1)
obj = serializer.decode(txt)

@TODO: Alternative name for encode/decode serialize/unserialize

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from json import JSONEncoder, JSONDecoder

# Contains classes that should be possible to encode and decode.
_cls_list = {}


def add(cls):
    """Add a class that should be possible to encode/decode."""
    _cls_list[cls.__name__] = cls


def encode(obj):
    """Encode/Serialize an object to a JSON."""
    return JSONEncoder(default=_encode_hook).encode(obj)


def decode(obj):
    """Dencode/Unserialize an object from a JSON."""
    return JSONDecoder(object_hook=_decode_hook).decode(obj)


def _encode_hook(obj):
    if obj.__class__.__name__ not in _cls_list:
        if not isinstance(obj, _cls_list[obj.__class__.__name__]):
            raise TypeError("%r is not JSON serializable" % (obj))

    obj.class_name = obj.__class__.__name__
    return obj.__dict__


def _decode_hook(value):
    obj = _cls_list[value['class_name']]()
    for key, val in value.iteritems():
        setattr(obj, key, val)

    return obj
