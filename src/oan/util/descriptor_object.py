#!/usr/bin/env python
"""
Abstract class used to create descriptor properties

Store variable information in instance __dict__.

Read more
    http://users.rcn.com/python/download/Descriptor.htm
"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.2"
__status__ = "Test"


class OANDescriptorObject(object):
    def name(self, name):
        return "%s_%s" % (name, id(self))

    def get_var(self, instance, name):
        key = self.name(name)
        if key not in instance.__dict__:
            raise AttributeError, key
        return instance.__dict__[key]

    def set_var(self, instance, name, value):
        instance.__dict__[self.name(name)] = value
