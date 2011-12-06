#!/usr/bin/env python
'''
Connection managment between nodes.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from twisted.protocols import basic
from twisted.internet import defer

from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientCreator
from twisted.protocols import amp

from oan_server import Sum

class OANClient():
    pass
def RemoteOANClientSum():
    def func1(p):
        result =  p.callRemote(Sum, a=13, b=81)
        return result

    def func2(result):
        return result['total']

    def done(result):
        print 'Done with math:', result

    d1 = ClientCreator(reactor, amp.AMP).connectTCP('127.0.0.1', 8000)
    d1.addCallback(func1)
    d1.addCallback(func2)

    defer.DeferredList([d1]).addCallback(done)

if __name__ == '__main__':
    RemoteOANClientSum()
    reactor.run()
