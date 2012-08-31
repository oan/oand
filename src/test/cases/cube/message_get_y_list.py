"""
"""
__author__ = "martin@amivono.com, daniel@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin@amivono.com, daniel@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from oan.util import log

from message import Message
from message_give_block_list import MessageGiveBlockListY
from message_redirect import MessageRedirect

class MessageGetYList(Message):
    pos = None

    def __init__(self, block_position):
        self.origin_position = block_position

    def is_in_block_with_y_list(self, app):
        '''
        Is in block who are in the same y list/direction as sender. Might even
        be the same block as the sender, but can't be the same slot.

        '''
        return (
            app.block_position.y <= self.origin_position.y and
            app.block_position.x == self.origin_position.x and
            self.origin_oan_id != app.cube_node.oan_id
        )

    def is_in_block_who_knows_block_with_y_list(self, app):
        return (
            app.block_position.y < self.origin_position.y and
            app.cube_view.x.has_slot(self.origin_position.x, 0)
        )

    def is_in_block_left_of_origin(self, app):
        return (
            app.block_position.y <= self.origin_position.y and
            app.block_position.x < self.origin_position.x
        )

    def forwards_y_list_back_to_origin(self, app):
        log.info("MessageGetYList step 3 to %s" % (self.origin_url,))
        app.send(self.origin_url, MessageGiveBlockListY( app.cube_view.y))

    def redirects_to_right_in_cube(self, app):
        log.info("MessageGetYList step 2 to %s" % app.cube_view.x.block_size(self.origin_position.x))
        msg = MessageRedirect(app.cube_view.x.get_slot(self.origin_position.x, 0), self)
        app.send(self.origin_url, msg)

    def redirects_up_in_cube(self, app):
        destination_node = None
        for y_pos in reversed(xrange(app.block_position.y)):
            log.info("y_pos %s" % y_pos)
            if app.cube_view.y.has_slot(y_pos, 0):
                destination_node = app.cube_view.y.get_slot(y_pos, 0)
                log.info("hit 1")
                break

        if not destination_node:
            for x_pos in reversed(xrange(app.block_position.x)):
                log.info("x_pos %s" % x_pos)
                if app.cube_view.x.has_slot(x_pos, 0):
                    destination_node = app.block_position.x.get_slot(x_pos, 0)
                    log.info("hit 2")
                    break

        log.info("MessageGetYList step 1 to %s" % (destination_node,))
        if destination_node:
            msg = MessageRedirect(destination_node, self)
            app.send(self.origin_url, msg)

    def execute(self, app):
        log.info("MessageGetYList slot:%s x:%s y:%s x_pos %s of %s y_pos %s of %s" % (
                 app.bind_url,
                 app.block_position.x, app.block_position.y,
                 self.origin_position.x, app.cube_view.x.size(),
                 self.origin_position.y, app.cube_view.y.size()
        ))
        log.info("x-list %s" % app.cube_view.x._blocks)
        log.info("y-list %s" % app.cube_view.y._blocks)

        if self.is_in_block_with_y_list(app):
            self.forwards_y_list_back_to_origin(app)

        elif self.is_in_block_who_knows_block_with_y_list(app):
            self.redirects_to_right_in_cube(app)

        else:
            self.redirects_up_in_cube(app)
