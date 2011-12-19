#!/usr/bin/env python

from twisted.internet.defer import Deferred
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory, ReconnectingClientFactory
from twisted.protocols import amp

from oan_amp_server import default_port
import oan_amp_commands

default_host = "localhost"

class OANAmpClientProtocol(amp.AMP):

    @oan_amp_commands.send.responder
    def send(self, data):
        """got send command from server"""
        self.factory.client.receive(data)
        return {'value': 'success'}

    def connectionMade(self):
        print self.factory
        self.factory.client.notify()

class OANAmpClientFactory(ReconnectingClientFactory):
    protocol = OANAmpClientProtocol
    client = None

    def __init__(self, client):
        self.client = client
        self.deferred = Deferred()

    def buildProtocol(self, addr):
        self.client.protocol = ClientFactory.buildProtocol(self, addr)
        self.client.protocol.factory = self
        return self.client.protocol

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection. retrying...'
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. retrying...:'
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                          reason)

class OANAmpClient(object):

    def __init__(self, host, port):
        self.protocol = None
        self.factory = None
        self.host = host
        self.port = port

    def connect(self):
        # koppla ned om den redan uppkopplad mot en server
        if self.protocol is not None:
            self.protocol.transport.loseConnection()

        self.factory = OANAmpClientFactory(self)
        connector = reactor.connectTCP(self.host, self.port, self.factory)
        self.factory.deferred.addCallback(self.connection_disconnected)
        return self.factory.deferred

    def disconnect(self):
        pass
        #self.factory.deferred.callback(self)

    def connection_disconnected(self, protocol):
        print "connection_disconnected - %s" % protocol

    def connect_fail(self, error):
        print "connect_fail - %s" % (error)
        #reactor.callLater(5, self.connect)


    '''

    notify server that my node is up and running

    '''
    def notify(self):
        deferred = self.protocol.callRemote(oan_amp_commands.notify)
        deferred.addCallback(self.notify_success)
        deferred.addErrback(self.notify_fail)

    def notify_success(self, result):
        print "notify_success (%s)" % result
        #for i in xrange(1):
        #    self.send_from_client("%d" % (i) )

    def notify_fail(self, error):
        print "notify_fail (%s)" % error



    '''
    send to server

    '''
    def send(self, text):
        if text and self.protocol is not None:
            deferred = self.protocol.callRemote(oan_amp_commands.send, data=text)
            deferred.addCallback(self.send_success)
            deferred.addErrback(self.send_fail)
            return deferred


    def send_success(self, result):
        print "success (%s)" % result
        return result

    def send_fail(self, error):
        print "fail (%s)" % error
        return error


    '''
        send loop
    '''

    def send_loop(self):
        text = "12:12:C"
        self.send(text);
        reactor.callLater(2, self.send_loop)


    '''
    got data from server
    '''
    def receive(self, data):
        print data


if __name__ == "__main__":
    c = OANAmpClient(default_host, default_port)
    c.connect()
    reactor.callWhenRunning(c.send_loop)
    reactor.run()
