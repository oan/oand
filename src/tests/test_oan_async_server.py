import unittest

import thread
import asyncore
import telnetlib
import exceptions

from EchoServer import EchoServer
from EchoClient import EchoClient


class TestEchoServer(unittest.TestCase):
    server = None
    poller = None

    def setUp(self):
        self.server = EchoServer('localhost', 8080)
        self.server.start()

    def tearDown(self):
        self.server.close()

    def test_foo(self):
        self.assertTrue(True)

    def test_foo2(self):
        self.assertTrue(True)

    # def test_echoserver_close(self):
    #     tn = telnetlib.Telnet('localhost', 8080)
    #     tn.write("close\n")
    #     self.assertRaises(exceptions.EOFError, tn.read_until, "muu", 30)
    #     tn.close()

    # def test_echoserver_moo(self):
    #     tn = telnetlib.Telnet('localhost', 8080)
    #     tn.write("moo\n")
    #     data = tn.read_until("muu", 30)
    #     self.assertEqual(data, "muu")
    #     tn.close()


    # def test_echoserver(self):
    #     tn = telnetlib.Telnet('localhost', 8080)

    #     #tn.read_until("login: ")
    #     tn.write("moo\n")
    #     tn.read_until("muu", 30)

    #     #print tn.read_all()
    #     #self.assertRaises(Exception, oan.validate)
    #     tn.close()

