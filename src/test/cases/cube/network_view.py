"""
"""
__author__ = "martin@amivono.com, daniel@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin@amivono.com, daniel@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from oan.util.decorator.accept import IGNORE, accepts, returns

from oan.util import log
from oan.util import log_counter
from network_counter import NetworkCounter

from block_position import BlockPosition
from cube_view import CubeView
from cube_node import OANCubeNode
from message import Message
from network_builder import NetworkBuilder


class Connections:
    """Roughly emulate a network and time."""

    """
    Holdes a reference to all nodes on the emulated network.
    key   - a bind url ie. "001"
    value - reference to node instance.

    """
    all = {}

    @staticmethod
    def clear():
        Connections.all = {}


class NetworkView():
    # Emulation of sockets this NetworkView is connected to.
    _sockets = None

    # Bind address to this NetworkView.
    _cube_node = None

    # Statistic counters.
    counter = None

    # Callback called when receiving messages.
    received_cb = None

    @accepts(IGNORE, OANCubeNode)
    def __init__(self, cube_node):
        self._sockets = {}
        self._cube_node = cube_node
        self.counter = NetworkCounter()
        self.received_cb = lambda network_view, message : None

        self.start_listening()

    def start_listening(self):
        '''Start listening for connections.'''
        log.info("%s starts listening." % (self._cube_node.url,))
        Connections.all[self._cube_node.url] = self

    def stop_listening(self):
        '''Stop listening for connections.'''
        log.info("%s stops listening." % self._cube_node.url,)
        del Connections.all[self._cube_node.url]

    def accepted(self, url, remote_network_view):
        log.info("%s accepted connection from %s" % (self._cube_node.url, url))
        self._sockets[url] = remote_network_view
        self.counter.accept += 1

    def closed(self, url):
        del self._sockets[url]
        self.counter.close += 1

    def connect(self, urls):
        for url in urls:
            if url not in self._sockets:
                if url in Connections.all:
                    log.info("%s connects to %s" % (self._cube_node.url, url))
                    self._sockets[url] = Connections.all[url]
                    self.counter.connect += 1

                    # Emulate connection from remote NetworkView.
                    if self._cube_node.url not in Connections.all[url]._sockets:
                        Connections.all[url].accepted(self._cube_node.url, self)

                else:
                    log.info("%s connects to %s failed" % (self._cube_node.url, url))

        for url in self._sockets.keys():
            if url not in urls:
                self._disconnect(url)

    def disconnect(self):
        for url in self._sockets.keys():
            self._disconnect(url)

    def send(self, url, message):
        log_counter.begin("%s send" % message.__class__.__name__)
        self.counter.send += 1
        log.info("%s sent %s to %s " % (self._cube_node.url, message.__class__.__name__, Connections.all[url]._cube_node.url))
        message.origin_oan_id = self._cube_node.oan_id
        message.origin_url = self._cube_node.url
        if url not in self._sockets:
            self.connect([url])
            # TODO
            # self.disconnect_and_forget_if_not_used(url, "5 minutes")

        log_counter.end("%s send" % message.__class__.__name__)
        self._sockets[url].receive(message)

    def push(self, urls, message):
        self.counter.push += 1
        for url in urls:
            self.send(url, message)

    def receive(self, message):
        log.info("%s received %s from %s " % (self._cube_node.url, message.__class__.__name__, message.origin_url))
        log_counter.begin("%s received" % message.__class__.__name__)
        self.counter.receive += 1
        self.received_cb(self, message)
        log_counter.end("%s received" % message.__class__.__name__)

    def _disconnect(self, url):
        self.counter.disconnect += 1
        log.info("%s disconnects from %s" % (self._cube_node.url, url))
        del self._sockets[url]

        # Close connection from remote NetworkView.
        if self._cube_node.url in Connections.all[url]._sockets:
            Connections.all[url].closed(self._cube_node.url)

    def connected(self):
        return len(self._sockets) > 0


from test.test_case import OANCubeTestCase


class MessageTest(Message):
    counter = None
    def __init__(self, counter):
        self.counter = counter

    def execute(self, network_view, result_counter):
        self.counter += 1
        result_counter[network_view._cube_node.url] = self.counter


class TestNetworkView(OANCubeTestCase):

    def test_network_connect(self):
        block_pos = BlockPosition(2, 2, 2)
        my_url = ('x', 2)
        cube_size = 30
        all_network_urls = []

        cube_view = CubeView(block_pos)
        for x in xrange(000, cube_size):
            cube_view.x.add(x, OANCubeNode(self.create_oan_id(x), ('x', x)))
            all_network_urls.append(('x', x))

        for y in xrange(000, cube_size):
            cube_view.y.add(y, OANCubeNode(self.create_oan_id(y), ('y', y)))
            all_network_urls.append(('y', y))

        for z in xrange(000, cube_size):
            cube_view.z.add(z, OANCubeNode(self.create_oan_id(z), ('z', z)))
            all_network_urls.append(('z', z))

        network_builder = NetworkBuilder(my_url, block_pos)
        network_builder.build(cube_view)

        all_network_urls.remove(my_url)

        # Emulate starting a network with several nodes.
        network_view = {}
        result_counter = {}
        for host, port in all_network_urls:
            result_counter[(host, port)] = {}
            network_view[(host, port)] = NetworkView(OANCubeNode(self.create_oan_id(port), (host, port)))
            network_view[(host, port)].received_cb = lambda nv, msg : msg.execute(
                nv, result_counter
            )

        # Create my node and connect to the emulated network.
        my_node = OANCubeNode(self.create_oan_id(2), my_url)
        network_view[my_url] = NetworkView(my_node)
        network_view[my_url].connect(network_builder.get_all())
        result_counter[my_url] = {}
        network_view[my_url].received_cb = lambda nv, msg : msg.execute(
            nv, result_counter
        )

        self.assertEqual(
            set(network_view[my_url]._sockets.keys()),
            set([('x', 1), ('x', 3), ('x', 17),
                 ('y', 1), ('y', 3), ('y', 17), ('y', 2),
                 ('z', 1), ('z', 3), ('z', 17), ('z', 2)])
        )

        #
        msg = MessageTest(5)
        network_view[my_url].send(('x', 1), msg)
        self.assertEqual(msg.counter, 6)
        self.assertEqual(result_counter[('x', 1)], 6)

        # Verify that my BFFs increase the counter.
        msg = MessageTest(10)
        network_view[my_url].push(network_builder.get_x(), msg)
        self.assertEqual(msg.counter, 13)
        self.assertEqual(result_counter[('x', 1)], 11)
        self.assertEqual(result_counter[('x', 3)], 12)
        self.assertEqual(result_counter[('x', 17)], 13)

        #
        msg = MessageTest(10)
        network_view[my_url].push(network_builder.get_y(), msg)
        self.assertEqual(msg.counter, 13)
        self.assertEqual(result_counter[('y', 1)], 11)
        self.assertEqual(result_counter[('y', 3)], 12)
        self.assertEqual(result_counter[('y', 17)], 13)

        #
        msg = MessageTest(10)
        network_view[my_url].push(network_builder.get_z(), msg)
        self.assertEqual(msg.counter, 13)
        self.assertEqual(result_counter[('z', 1)], 11)
        self.assertEqual(result_counter[('z', 3)], 12)
        self.assertEqual(result_counter[('z', 17)], 13)

        #
        msg = MessageTest(10)
        network_view[my_url].push(network_builder.get_block(), msg)
        self.assertEqual(msg.counter, 12)
        self.assertEqual(result_counter[('y', 2)], 11)
        self.assertEqual(result_counter[('z', 2)], 12)

        # Verify that the remote socket is connected to me.
        self.assertTrue(my_url in Connections.all[('y', 17)]._sockets)
        self.assertTrue(my_url in Connections.all[('y', 3)]._sockets)
        self.assertTrue(my_url in Connections.all[('x', 17)]._sockets)
        self.assertTrue(my_url in Connections.all[('y', 2)]._sockets)
        self.assertTrue(my_url in Connections.all[('z', 17)]._sockets)
        self.assertTrue(my_url in Connections.all[('y', 1)]._sockets)
        self.assertTrue(my_url in Connections.all[('x', 3)]._sockets)
        self.assertTrue(my_url in Connections.all[('z', 3)]._sockets)
        self.assertTrue(my_url in Connections.all[('z', 2)]._sockets)
        self.assertTrue(my_url in Connections.all[('z', 1)]._sockets)
        self.assertTrue(my_url in Connections.all[('x', 1)]._sockets)

        # Disconnect from everyone.
        network_view[my_url].disconnect()
        self.assertEqual(
            set(network_view[my_url]._sockets.keys()),
            set([])
        )

        # Verify that the remote socket is no longer connected to me.
        self.assertTrue(my_url not in Connections.all[('y', 17)]._sockets)
        self.assertTrue(my_url not in Connections.all[('y', 3)]._sockets)
        self.assertTrue(my_url not in Connections.all[('x', 17)]._sockets)
        self.assertTrue(my_url not in Connections.all[('y', 2)]._sockets)
        self.assertTrue(my_url not in Connections.all[('z', 17)]._sockets)
        self.assertTrue(my_url not in Connections.all[('y', 1)]._sockets)
        self.assertTrue(my_url not in Connections.all[('x', 3)]._sockets)
        self.assertTrue(my_url not in Connections.all[('z', 3)]._sockets)
        self.assertTrue(my_url not in Connections.all[('z', 2)]._sockets)
        self.assertTrue(my_url not in Connections.all[('z', 1)]._sockets)
        self.assertTrue(my_url not in Connections.all[('x', 1)]._sockets)

