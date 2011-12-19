#!/usr/bin/env python
'''
Test cases for twisted deffered callback.

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from twisted.internet.defer import Deferred
from twisted.internet.error import ConnectError
from twisted.internet.protocol import ClientFactory, ServerFactory, Protocol
from twisted.trial.unittest import TestCase

class Sum(amp.Command):
    arguments = [('a', amp.Integer()),
                 ('b', amp.Integer())]
    response = [('total', amp.Integer())]

class PoetryServerProtocol(amp.AMP):
    @Sum.responder
    def sum(self, a, b):
        total = a + b
        print 'Did a sum: %d + %d = %d' % (a, b, total)
        return {'total': total}

#class PoetryServerProtocol(Protocol):
#
#    def connectionMade(self):
#        self.transport.write(self.factory.poem)
#        self.transport.loseConnection()

class PoetryServerFactory(ServerFactory):

    protocol = PoetryServerProtocol

    def __init__(self, poem):
        self.poem = poem


class PoetryClientProtocol(amp.AMP):
    @Sum.responder
    def sum(self, a, b):
        total = a + b
        print 'Did a sum: %d + %d = %d' % (a, b, total)
        return {'total': total}


class PoetryClientFactory(ClientFactory):

    protocol = PoetryClientProtocol

    def __init__(self):
        self.deferred = Deferred()

    def poem_finished(self, poem):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.callback(poem)

    def clientConnectionFailed(self, connector, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)


def get_poetry(host, port):
    from twisted.internet import reactor
    factory = PoetryClientFactory()
    reactor.connectTCP(host, port, factory)
    return factory.deferred

class PoetryTestCase(TestCase):

    def setUp(self):
        factory = PoetryServerFactory(TEST_POEM)
        from twisted.internet import reactor
        self.port = reactor.listenTCP(0, factory, interface="127.0.0.1")
        self.portnum = self.port.getHost().port

    def tearDown(self):
        port, self.port = self.port, None
        return port.stopListening()

    def _test_client(self):
        """The correct poem is returned by get_poetry."""
        d = get_poetry('127.0.0.1', self.portnum)

        def got_poem(poem):
            self.assertEquals(poem, TEST_POEM)

        d.addCallback(got_poem)

        return d

    def test_failure(self):
        """The correct failure is returned by get_poetry when
        connecting to a port with no server."""
        d = get_poetry('127.0.0.1', 0)
        return self.assertFailure(d, ConnectError)
