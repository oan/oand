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

from amp.oan_amp_server import OANAmpServer
from amp.oan_amp_client import OANAmpClient


class OANAmpTestCase(TestCase):
    server = None
    client = None

    def setUp(self):
        pass
        #self.server = OANAmpServer(8000);
        #self.server.start()

        #self.client = OANAmpClient('localhost', 8000)
        #self.client.connect()

    def tearDown(self):
        pass
        #self.client.disconnect()
        #return self.server.stop()

    def test_client(self):
        pass
        """The correct poem is returned by get_poetry."""
        #from twisted.internet import reactor
        #reactor.callWhenRunning(self.server.send_loop)

        self.client = OANAmpClient('localhost', 8000)
        self.client.connect()
        d = self.client.send('a message')
        return d
