"""
"""
__author__ = "martin@amivono.com, daniel@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin@amivono.com, daniel@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from test.test_case import OANTestCase
from oan.util import log
from oan.util import log_counter
from network_counter import NetworkCounter

from block_position import BlockPosition
from cube_view import CubeView
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
    _bind_url = None

    # Statistic counters.
    counter = None

    # Callback called when receiving messages.
    received_cb = None

    def __init__(self, bind_url):
        self._sockets = {}
        self._bind_url = bind_url
        self.counter = NetworkCounter()
        self.received_cb = lambda network_view, message : None

        self.start_listening()

    def start_listening(self):
        '''Start listening for connections.'''
        log.info("%s starts listening." % self._bind_url)
        Connections.all[self._bind_url] = self

    def stop_listening(self):
        '''Stop listening for connections.'''
        log.info("%s stops listening." % self._bind_url)
        del Connections.all[self._bind_url]

    def accepted(self, url, remote_network_view):
        self._sockets[url] = remote_network_view
        self.counter.accept += 1

    def closed(self, url):
        del self._sockets[url]
        self.counter.close += 1

    def connect(self, urls):
        for url in urls:
            if url not in self._sockets:
                if url in Connections.all:
                    log.info("%s connects to %s" % (self._bind_url, url))
                    self._sockets[url] = Connections.all[url]
                    self.counter.connect += 1

                    # Emulate connection from remote NetworkView.
                    if self._bind_url not in Connections.all[url]._sockets:
                        Connections.all[url].accepted(self._bind_url, self)

                else:
                    log.info("%s connects to %s failed" % (self._bind_url, url))

        for url in self._sockets.keys():
            if url not in urls:
                self._disconnect(url)

    def disconnect(self):
        for url in self._sockets.keys():
            self._disconnect(url)

    def send(self, url, message):
        log_counter.begin("%s send" % message.__class__.__name__)
        self.counter.send += 1
        log.info("%s sent %s to %s " % (self._bind_url, message.__class__.__name__, Connections.all[url]._bind_url))
        message.origin_url = self._bind_url
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
        log.info("%s received %s from %s " % (self._bind_url, message.__class__.__name__, message.origin_url))
        log_counter.begin("%s received" % message.__class__.__name__)
        self.counter.receive += 1
        self.received_cb(self, message)
        log_counter.end("%s received" % message.__class__.__name__)

    def _disconnect(self, url):
        self.counter.disconnect += 1
        log.info("%s disconnects from %s" % (self._bind_url, url))
        del self._sockets[url]

        # Close connection from remote NetworkView.
        if self._bind_url in Connections.all[url]._sockets:
            Connections.all[url].closed(self._bind_url)

    def connected(self):
        return len(self._sockets) > 0


class MessageTest(Message):
    counter = None
    def __init__(self, counter):
        self.counter = counter

    def execute(self, network_view, result_counter):
        self.counter += 1
        result_counter[network_view._bind_url] = self.counter


class TestNetworkView(OANTestCase):

    def dis_test_network_connect(self):
        block_pos = BlockPosition(2, 2, 2)
        bind_url = "X.002"
        cube_size = 30
        all_network_urls = []

        cube_view = CubeView(block_pos)
        for x in xrange(000, cube_size):
            cube_view.x.add(x, "X.{0:0>3}".format(x))
            all_network_urls.append("X.{0:0>3}".format(x))

        for y in xrange(000, cube_size):
            cube_view.y.add(y, "Y.{0:0>3}".format(y))
            all_network_urls.append("Y.{0:0>3}".format(y))

        for z in xrange(000, cube_size):
            cube_view.z.add(z, "Z.{0:0>3}".format(z))
            all_network_urls.append("Z.{0:0>3}".format(z))

        network_builder = NetworkBuilder(bind_url, block_pos)
        network_builder.build(cube_view)

        all_network_urls.remove(bind_url)
        network_view = {}
        result_counter = {}
        for url in all_network_urls:
            result_counter[url] = {}
            network_view[url] = NetworkView(url)
            network_view[url].received_cb = lambda nv, msg : msg.execute(
                nv, result_counter
            )

        network_view[bind_url] = NetworkView(bind_url)
        network_view[bind_url].connect(network_builder.get_all())
        result_counter[bind_url] = {}
        network_view[bind_url].received_cb = lambda nv, msg : msg.execute(
            nv, result_counter
        )
        self.assertEqual(
            set(network_view[bind_url]._sockets.keys()),
            set(['X.001', 'X.003', 'X.017',
                 'Y.001', 'Y.003', 'Y.017', 'Y.002',
                 'Z.001', 'Z.003', 'Z.017', 'Z.002'])
        )

        #
        msg = MessageTest(5)
        network_view[bind_url].send("X.001", msg)
        self.assertEqual(msg.counter, 6)
        self.assertEqual(result_counter["X.001"], 6)

        # Verify that my BFFs increase the counter.
        msg = MessageTest(10)
        network_view[bind_url].push(network_builder.get_x(), msg)
        self.assertEqual(msg.counter, 13)
        self.assertEqual(result_counter["X.001"], 11)
        self.assertEqual(result_counter["X.003"], 12)
        self.assertEqual(result_counter["X.017"], 13)

        #
        msg = MessageTest(10)
        network_view[bind_url].push(network_builder.get_y(), msg)
        self.assertEqual(msg.counter, 13)
        self.assertEqual(result_counter["Y.001"], 11)
        self.assertEqual(result_counter["Y.003"], 12)
        self.assertEqual(result_counter["Y.017"], 13)

        #
        msg = MessageTest(10)
        network_view[bind_url].push(network_builder.get_z(), msg)
        self.assertEqual(msg.counter, 13)
        self.assertEqual(result_counter["Z.001"], 11)
        self.assertEqual(result_counter["Z.003"], 12)
        self.assertEqual(result_counter["Z.017"], 13)

        #
        msg = MessageTest(10)
        network_view[bind_url].push(network_builder.get_block(), msg)
        self.assertEqual(msg.counter, 12)
        self.assertEqual(result_counter["Y.002"], 11)
        self.assertEqual(result_counter["Z.002"], 12)

        # Verify that the remote socket is connected to me.
        self.assertTrue(bind_url in Connections.all["Y.017"]._sockets)
        self.assertTrue(bind_url in Connections.all["Y.003"]._sockets)
        self.assertTrue(bind_url in Connections.all["X.017"]._sockets)
        self.assertTrue(bind_url in Connections.all["Y.002"]._sockets)
        self.assertTrue(bind_url in Connections.all["Z.017"]._sockets)
        self.assertTrue(bind_url in Connections.all["Y.001"]._sockets)
        self.assertTrue(bind_url in Connections.all["X.003"]._sockets)
        self.assertTrue(bind_url in Connections.all["Z.003"]._sockets)
        self.assertTrue(bind_url in Connections.all["Z.002"]._sockets)
        self.assertTrue(bind_url in Connections.all["Z.001"]._sockets)
        self.assertTrue(bind_url in Connections.all["X.001"]._sockets)

        # Disconnect from everyone.
        network_view[bind_url].disconnect()
        self.assertEqual(
            set(network_view[bind_url]._sockets.keys()),
            set([])
        )

        # Verify that the remote socket is no longer connected to me.
        self.assertTrue(bind_url not in Connections.all["Y.017"]._sockets)
        self.assertTrue(bind_url not in Connections.all["Y.003"]._sockets)
        self.assertTrue(bind_url not in Connections.all["X.017"]._sockets)
        self.assertTrue(bind_url not in Connections.all["Y.002"]._sockets)
        self.assertTrue(bind_url not in Connections.all["Z.017"]._sockets)
        self.assertTrue(bind_url not in Connections.all["Y.001"]._sockets)
        self.assertTrue(bind_url not in Connections.all["X.003"]._sockets)
        self.assertTrue(bind_url not in Connections.all["Z.003"]._sockets)
        self.assertTrue(bind_url not in Connections.all["Z.002"]._sockets)
        self.assertTrue(bind_url not in Connections.all["Z.001"]._sockets)
        self.assertTrue(bind_url not in Connections.all["X.001"]._sockets)

