#!/usr/bin/env python

import sys

from twisted.protocols import amp
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory
from twisted.python import usage
import oan.amp_commands

default_port = 65432

class OANAmpServerProtocol(amp.AMP):

    @oan_amp_commands.notify.responder
    def notify(self):
        print "notify"
        self.factory.server.clients["node1"] = self;
        return {'value': 'notify success'}

    @oan_amp_commands.send.responder
    def send(self, data):
        self.factory.server.receive(data)
        return {'value': 'send success'}

    def connectionLost(self, unused):
        print "connectionLost node remove"
        del self.factory.server.clients["node1"]


class OANAmpServerFactory(ServerFactory):
    protocol = OANAmpServerProtocol
    server = None

    def __init__(self, server):
        self.server = server


class OANAmpServer(object):
    protocol = None
    port = None
    connector = None
    factory = None
    clients = {}

    def __init__(self, port):
        self.port = port

    def start(self):
        self.factory = OANAmpServerFactory(self)
        self.connector = reactor.listenTCP(self.port, self.factory)

    def stop(self):
        connector, self.connector = self.connector, None
        return connector.stopListening()

    def send_loop(self):
        if "node1" in self.clients:
            client_protocol = self.clients["node1"]
            text = "12:12:S"
            deferred = client_protocol.callRemote(oan_amp_commands.send, data=text)
            deferred.addCallback(self.send_loop_success)
            deferred.addErrback(self.send_loop_fail)
        else:
            reactor.callLater(2, self.send_loop)

    def send_loop_success(self, result):
        reactor.callLater(2, self.send_loop)

    def send_loop_fail(self, result):
        print "fail (%s)" % result
        reactor.callLater(2, self.send_loop)


    '''
    got data from client
    '''
    def receive(self, data):
        print data


if __name__ == "__main__":
    server = OANAmpServer(default_port)
    server.start()
    reactor.callWhenRunning(server.send_loop)
    reactor.run()
