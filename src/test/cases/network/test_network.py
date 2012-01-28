#!/usr/bin/env python
'''
Test communication (network, bridges, server etc.) between nodes.

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import socket
from uuid import UUID
from Queue import Queue

import oan
from oan import dispatch, node_mgr
from oan.dispatcher.message import OANMessagePing
from oan.dispatcher.command import OANCommandSendToNode
from oan.application import OANApplication
from oan.config import OANConfig

from test.test_case import OANTestCase


# test and see what happends if n1 connects to n2 at same time as n2 connect to n1.
class TestOANNetwork(OANTestCase):
    queue = None
    app = None


    def setUp(self):
        self.queue = Queue()

        self.app = OANApplication(OANConfig(
            '00000000-0000-0000-8000-000000000000',
            "TestOAN",
            "localhost",
            str(8000)
        ))

        self.app.run()
        self.create_node()
        self.create_watcher()

    def tearDown(self):
        self.app.stop()
        self.queue = None


    def get_local_host(self):
        """
        Should be moved to OANTestCase or a util module to use in all unittest.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        host = s.getsockname()[0]
        s.close()
        return host


    def create_node(self):
        """Create known nodes (instead of loading from db"""
        node_mgr().create_node(UUID('00000000-0000-0000-4000-000000000000'), self.get_local_host(), 4000, False)
        node_mgr().create_node(UUID('00000000-0000-0000-4001-000000000000'), self.get_local_host(), 4001, False)
        node_mgr().create_node(UUID('00000000-0000-0000-4002-000000000000'), self.get_local_host(), 4002, False)
        node_mgr().create_node(UUID('00000000-0000-0000-4003-000000000000'), self.get_local_host(), 4003, False)

    def got_message(self, message):
        if isinstance(message, OANMessagePing):
            if message.ping_counter == 1:
                self.queue.put(message)



    def create_watcher(self):
        dispatch().on_message.append(self.got_message)



    def test_message_ping(self):
        self.assertTrue(True)

        # Send a ping between all nodes 5x10 times.
        for n in xrange(4000, 4001):
            for i in xrange(5):
                dispatch().execute(OANCommandSendToNode.create(
                    UUID('00000000-0000-0000-%s-000000000000' % n),
                    OANMessagePing.create( "N%dP%d" % (n, i), 10 )
                ))

        counter = 0
        for i in xrange(20):
            message = self.queue.get()
            counter += 1
            print counter

        self.assertEqual(counter, 20)  # 4 * 5



# #!/usr/bin/env python
# '''
# RPC server handling request from oan clients.

# '''

# __author__ = "martin.palmer.develop@gmail.com"
# __copyright__ = "Copyright 2011, Amivono AB"
# __maintainer__ = "martin.palmer.develop@gmail.com"
# __license__ = "We pwn it all."
# __version__ = "0.1"
# __status__ = "Test"

# import asyncore
# import socket
# import time
# import datetime

# from test.test_case import OANTestCase
# from oan.event import OANEvent
# from collections import deque

# import asyncore, asynchat
# import os, socket, string

# from datetime import datetime


# class OANBridge(asyncore.dispatcher):

#     on_receive_line = None
#     on_send_line = None

#     def __init__(self, addr, sock = None):
#         asyncore.dispatcher.__init__(self, sock)

#     def handle_connect(self):
#         pass

#     def handle_read(self):
#         pass

#     def writable(self):
#         pass

#     def handle_write(self):
#         pass

#     def handle_close(self):
#         pass

#     def handle_error(self):
#         pass

#     def shutdown(self):
#         pass



# class OANListen(asyncore.dispatcher):


#     def __init__(self, host, port):
#         asyncore.dispatcher.__init__(self)

#     def handle_accept(self):
#         server.add_bridge
#         pass

#     def handle_close(self):
#         pass

#     def handle_error(self):
#         server.on_error()
#         pass

#     def shutdown(self):
#         pass


# class OANServer:

#     # skall skicka in som map till asyncore.
#     bridges = {}

#     def add_bridge(self, bridge):
#         self.bridges[bridge.node_oan_id] = bridge

#     def connect(host, port):
#         bridge = OANBridge(self, host, port)

#     def send(node, message):
#         if (node not connected)


#         self.bridges[node_oan_id].send(message)



# class OANNetworkWorker(Thread):
#     _server = None
#     _passthru = None

#     def __init__(self, passthru):
#         self._passthru = passthru

#     def run(self):
#         self._server = OANServer()
#         while(true):
#             message = _passthru.get()
#             message.execute(server)

#         pass

# class TestOANServer(OANTestCase):
#     def test_xxx(self):


# class TestOANNetwork(OANTestCase):
#     ping_queue = Queue()



#     def setup(self):
#         network = OANNetwork()
#         network.on_receive.append(ping_received)

#         message_listen = OANNetworkMessageListen.create(1337))
#         network.execute(message_listen)


#     def teardown(self):
#         network.shutdown()



#     def ping_received(self, message):
#         ping_queue.put(message)


#     def test_send(self):
#         message_ping = MessagePing.create("unittest-ping", ping_counter = 5):

#         oan_id = UUID("00000000-0000-cccc-0000-000000000000")
#         node = OANNetworkNode.create(oan_id, "localhost", 1338, False):

#         node.send(message_ping)

#         if node.is_disconnected():
#             message_connect = NetworksMessageConnectToNode.create(node))
#             network.execute(message_connect)

#         message_ping_received = ping_queue.get()

#         self.assertEqual(message_ping_received.__class__, MessagePing)
#         self.assertEqual(message_ping_received.node_oan_id, oan_id)
#         self.assertEqual(message_ping_received.ping_id, "unittest-ping")
#         self.assertEqual(message_ping_received.ping_counter, 4)


#     # def test_ping(self):
#     #     message_ping = MessagePing.create("unittest-ping", ping_counter = 5):
#     #     oan_id = UUID("00000000-0000-cccc-0000-000000000000")
#     #     node_mgr().send(oan_id, message_ping)

#     #     message_ping_received = ping_queue.get()

#     #     self.assertEqual(message_ping_received.__class__, MessagePing)
#     #     self.assertEqual(message_ping_received.node_oan_id, oan_id)
#     #     self.assertEqual(message_ping_received.ping_id, "unittest-ping")
#     #     self.assertEqual(message_ping_received.ping_counter, 4)













