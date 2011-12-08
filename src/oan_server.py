#!/usr/bin/env python
'''
RPC server handling request from oan clients.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from twisted.protocols import basic
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.python import log
from twisted.protocols import amp
import sys
from twisted.internet import reactor
from twisted.internet.protocol import Factory

class OANServer():
    pass

class Sum(amp.Command):
    arguments = [('a', amp.Integer()),
                 ('b', amp.Integer())]
    response = [('total', amp.Integer())]

class RemoteOANProtocol(amp.AMP):
    @Sum.responder
    def sum(self, a, b):
        total = a + b
        print 'Did a sum: %d + %d = %d' % (a, b, total)
        return {'total': total}

class RemoteOANFactory(protocol.Factory):
    protocol = RemoteOANProtocol

def main():
    log.startLogging(sys.stdout)
    reactor.listenTCP(8000, RemoteOANFactory())
    reactor.run()

if __name__ == "__main__":
    main()
