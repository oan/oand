"""
"""
__author__ = "martin@amivono.com, daniel@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin@amivono.com, daniel@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from cube_constants import *

from oan.util import log

from block_position import BlockPosition
from message import Message
from message_give_block_list import MessageGiveBlockListX, MessageGiveBlockListY, MessageGiveBlockListZ
from message_give_block_position import MessageGiveBlockPosition
from message_redirect import MessageRedirect


class MessageConnect(Message):

    def get_x_size(self, block_list_y):
        """
        The maximum number of blocks in x direction is equal to the maximum
        number of blocks in y direction + 1. The result of this is that
        when the y direction expands with one block, the x direction will
        also automatically expand.

        """
        last_block_cord = block_list_y.size()-1
        slots_in_last_block = block_list_y.block_size(last_block_cord)

        if slots_in_last_block < MAX_SLOTS_IN_BLOCK:
            return max(3, last_block_cord)
        else:
            return max(3, last_block_cord+1)

    def add_url_to_current_x_list(self, app, origin_url, x_pos):
        """
        Add url to first free slot on existing blocks in x direction.

        """
        log.info("add_url_to_current_x_list x: %s y: %s" % (x_pos, app.block_position.y) )

        block = app.cube_view.x.get_block(x_pos)
        block.append(origin_url)

        msg = MessageGiveBlockPosition(app, BlockPosition(x_pos, app.block_position.y, 0))
        app.send(origin_url, msg)
        app.push(app.network_builder.get_x(), MessageGiveBlockListX(app.cube_view.x))
        app.push(app.network_builder.get_y(), MessageGiveBlockListY(app.cube_view.y))
        app.push(app.network_builder.get_z(), MessageGiveBlockListZ(app.cube_view.z))

        app.push(app.network_builder.get_block(), MessageGiveBlockListX(app.cube_view.x))
        app.push(app.network_builder.get_block(), MessageGiveBlockListY(app.cube_view.y))
        app.push(app.network_builder.get_block(), MessageGiveBlockListZ(app.cube_view.z))

    def add_url_to_expanded_x_list(self, app, origin_url):
        """
        Expand the number of blocks in the x direction, and add the url to
        the last block.

        """
        app.cube_view.x.add(app.cube_view.x.size(), self.origin_url)
        log.info("expand cube_view.x with %s, cube_view.{x,y}.size: %s %s" % (
            origin_url, app.cube_view.x.size(), app.cube_view.y.size()
        ))

        msg = MessageGiveBlockPosition(app, BlockPosition(app.cube_view.x.size()-1, app.block_position.y, 0))
        app.send(origin_url, msg)

        # Will push the new CubeView before the network rebuild has been
        # executed on this application. This is good because then our old
        # friends will not reconnect to us if the cube has been changed in
        # such a way that we should no longer be connected to each other.
        # Or else they would try to reconnect to us if the x-list sync in the
        # cube is delayed, and this application would be required to disconnect.
        app.push(app.network_builder.get_x(),     MessageGiveBlockListX(app.cube_view.x))
        app.push(app.network_builder.get_block(), MessageGiveBlockListX(app.cube_view.x))


    def add_url_to_expanded_y_list(self, app, origin_url):
        """
        Expand the number of blocks in the y direction, and add the url to
        the last block.

        """
        app.cube_view.y.add(app.cube_view.y.size(), origin_url)
        log.info("expand cube_view.y with %s, cube_view.{x,y}.size: %s %s" % (
            origin_url, app.cube_view.x.size(), app.cube_view.y.size()
        ))

        msg = MessageGiveBlockPosition(app, BlockPosition(0, app.cube_view.y.size()-1, 0))
        app.send(origin_url, msg)

        # Will push the new CubeView before the network rebuild has been
        # executed on this application. This is good because then our old
        # friends will not reconnect to us if the cube has been changed in
        # such a way that we should no longer be connected to each other.
        # Or else they would try to reconnect to us if the y-list sync in the
        # cube is delayed, and this application would be required to disconnect.
        app.push(app.network_builder.get_y(),     MessageGiveBlockListY(app.cube_view.y))
        app.push(app.network_builder.get_block(), MessageGiveBlockListY(app.cube_view.y))

    def redirect_to_next_y_block(self, app, origin_url):
        """
        The current applications all slots on all blocks are occupied. Redirect
        to an url on the next block on y list. Let the connecting application
        ask the application on that url for a free slot.

        """
        log.info("redirect_to_next_y_block x:%s y:%s" % (app.cube_view.x.size(), app.cube_view.y.size()))
        msg = MessageRedirect(app.cube_view.y.get(app.block_position.y + 1, 0), self)
        app.send(origin_url, msg)

    def execute(self, app):
        x_max_size = self.get_x_size(app.cube_view.y)

        log.info("X-max-size: %s, cube_view.x.size: %s, cube_view.y.size: %s" % (
                 x_max_size, app.cube_view.x.size(), app.cube_view.y.size()))

        for x_pos in xrange(0, app.cube_view.x.size()):
            block = app.cube_view.x.get(x_pos)

            if len(block) < MAX_SLOTS_IN_BLOCK:
                self.add_url_to_current_x_list(app, self.origin_url, x_pos)
                return

        if app.cube_view.x.size() == x_max_size:
            if app.cube_view.y.size() <= app.block_position.y + 1:
                self.add_url_to_expanded_y_list(app, self.origin_url)
            else:
                self.redirect_to_next_y_block(app, self.origin_url)
        else:
            self.add_url_to_expanded_x_list(app, self.origin_url)
