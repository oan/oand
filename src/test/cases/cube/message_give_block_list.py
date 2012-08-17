"""
"""
__author__ = "martin@amivono.com, daniel@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin@amivono.com, daniel@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"


from oan.util import log
from oan.util import log_counter

from block_list import BlockList
from message import Message


class MessageGiveBlockList(Message):
    """
    Does a full sync between two nodes, and forwards new block_list to friends.

    TODO: Possible to only forward changes to friends, with a hash of
          block_list before new slots where merged with this cube_view. So
          friend can decide if it needs a full sync.
    """
    block_list = None

    def __init__(self, block_list):
        self.block_list = BlockList()
        self.block_list.merge_block_list(block_list)


class MessageGiveBlockListX(MessageGiveBlockList):
    def execute(self, app):
        log.info("On %s Merge list X" % (app.bind_url))
        if app.cube_view.x.merge_block_list(self.block_list):
            log_counter.begin("GiveBlockListX Forward ")
            app.push(app.network_builder.get_x(), self)
            app.connect()
            log_counter.end("GiveBlockListX Forward ")
        else:
            log_counter.hit("GiveBlockListX Not needed")


class MessageGiveBlockListY(MessageGiveBlockList):
    def execute(self, app):
        log.info("On %s Merge list Y" % (app.bind_url))
        if app.cube_view.y.merge_block_list(self.block_list):
            log_counter.begin("GiveBlockListY Forward")
            app.push(app.network_builder.get_y(), self)
            app.connect()
            log_counter.end("GiveBlockListY Forward")
        else:
            log_counter.hit("GiveBlockListY Not needed")


class MessageGiveBlockListZ(MessageGiveBlockList):
    def execute(self, app):
        log.info("On %s Merge list Z" % (app.bind_url))
        if app.cube_view.z.merge_block_list(self.block_list):
            log_counter.begin("GiveBlockListZ Forward")
            app.push(app.network_builder.get_z(), self)
            app.connect()
            log_counter.end("GiveBlockListZ Forward")
        else:
            log_counter.hit("GiveBlockListZ Not needed")
