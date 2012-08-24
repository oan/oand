"""
"""
__author__ = "martin@amivono.com, daniel@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin@amivono.com, daniel@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from uuid import UUID
from oan.util import log

from cube_node import OANCubeNode
from block_position import BlockPosition
from cube_view import CubeView
from network_builder import NetworkBuilder
from network_view import NetworkView


class OANApplication:
    bind_url = None
    cube_node = None
    cube_view = None
    block_position = None
    network_builder = None
    network_view = None

    def _create_uuid(self):
        (host, port) = self.bind_url
        return UUID("00000000-0000-0000-0000-00000000{0:04d}".format(port))

    def __init__(self, bind_url):
        self.bind_url = bind_url

        self.cube_node = OANCubeNode(self._create_uuid(), self.bind_url)
        self.cube_view = CubeView()
        self.network_view = NetworkView(self.cube_node)
        self.network_view.received_cb = self.received_cb

        self.set_block_position(BlockPosition(0, 0, 0))
        self.cube_view.b.append(self.cube_node)

    def set_block_position(self, block_position):
        self.block_position = block_position
        self.cube_view.set_block_position(self.block_position)
        self.network_builder = NetworkBuilder(self.bind_url, self.block_position)

    def connect(self):
        self.network_builder.build(self.cube_view)
        self.network_view.connect(self.network_builder.get_all())

    def send(self, url, message):
        self.network_view.send(url, message)

    def push(self, urls, message):
        self.network_view.push(urls, message)

    def received_cb(self, network_view, message):
        log.info("%s execute %s" % (self.bind_url, message.__class__.__name__))
        log.indent += 1
        message.execute(self)
        log.indent -= 1
        log.info("")

    def trigger_5minute_cron(self):
        """
        Called every 5 minute.

        Reconnect if nodes has been disconnected, or new node are online.

        """
        #self.connect()
        pass

