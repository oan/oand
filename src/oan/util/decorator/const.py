#!/usr/bin/env python
"""
Constants in python.

Read more
    http://stackoverflow.com/questions/2682745/creating-constant-in-python
"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.2"
__status__ = "Test"

def const(f):
    def fset(self, value):
        raise SyntaxError
    def fget(self):
        return f()
    return property(fget, fset)
