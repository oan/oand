#!/usr/bin/env python
'''
Event subscription.

A list of callable objects. Calling an instance of this will cause a
call to each item in the list in ascending order by index.

Example Usage:
>>> def f(x):
...     print 'f(%s)' % x
>>> def g(x):
...     print 'g(%s)' % x
>>> e = OANEvent()
>>> e()
>>> e.append(f)
>>> e(123)
f(123)
>>> e.remove(f)
>>> e()
>>> e += (f, g)
>>> e(10)
f(10)
g(10)
>>> del e[0]
>>> e(2)
g(2)

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

class OANEvent(list):
    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)

    def empty(self):
        return len(self) == 0

    def __repr__(self):
        return "Event(%s)" % list.__repr__(self)
