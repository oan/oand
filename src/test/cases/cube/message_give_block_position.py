"""
"""
__author__ = "martin@amivono.com, daniel@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin@amivono.com, daniel@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from oan.util import log

from cube_view import CubeView
from message import Message
from message_get_y_list import MessageGetYList
from message_give_block_list import MessageGiveBlockListX, MessageGiveBlockListY, MessageGiveBlockListZ


class MessageGiveBlockPosition(Message):
    """
    The connecting application will receive a cube_view from it's server. And
    then connect to the network.

    """
    block_position = None
    cube_view = None

    def __init__(self, app, block_position):
        self.block_position = block_position
        self.create_cube_view(app)

    def create_cube_view(self, app):
        """
        Create a cube view in the perspective of who the connecting application
        will see the cube.

        """
        self.cube_view = CubeView(self.block_position)

        x_pos, y_pos, z_pos = self.block_position.id()
        if y_pos == app.block_position.y:
            self.cube_view.x.merge_block_list(app.cube_view.x)
        else:
            self.cube_view.x.merge_block(x_pos, app.cube_view.y.get(y_pos))

        if x_pos == app.block_position.x:
            self.cube_view.y.merge_block_list(app.cube_view.y)
        else:
            self.cube_view.y.merge_block(y_pos, app.cube_view.x.get(x_pos))

        # TODO Z

    def execute(self, app):
        log.info("%s got block position: %s" % (app.bind_url, self.block_position.id()))
        log.info("%s got cubeview.x: %s" % (app.bind_url, self.cube_view.x.get_blocks()))
        app.set_block_position(self.block_position)
        app.cube_view.set_cube_view(self.cube_view)
        log.info("%s has cubeview.x: %s" % (app.bind_url, app.cube_view.x.get_blocks()))

        #todo self.sync_x_list(app)
        self.sync_y_list(app)

        app.connect()

        app.push(app.network_builder.get_x(), MessageGiveBlockListX(app.cube_view.x))
        app.push(app.network_builder.get_y(), MessageGiveBlockListY(app.cube_view.y))
        app.push(app.network_builder.get_z(), MessageGiveBlockListZ(app.cube_view.z))

        app.push(app.network_builder.get_block(), MessageGiveBlockListX(app.cube_view.x))
        app.push(app.network_builder.get_block(), MessageGiveBlockListY(app.cube_view.y))
        app.push(app.network_builder.get_block(), MessageGiveBlockListZ(app.cube_view.z))

    def empty_list(self, app, block_list):
        """Check if atleast on slot is occupied in block_list"""
        for block in block_list.get_blocks():
            if len(block) > 0 and app.bind_url not in block:
                return False
        return True

    def sync_y_list(self, app):
        log.info("whats in y %s %s" % (app.cube_view.y.get_blocks(), app.block_position.y))
        if self.empty_list(app, app.cube_view.y) and app.block_position.y != 0:
            log.info("sync_y_list-begin")
            # TODO handle if left block is empty.
            left_origin_url = app.cube_view.x.get(app.block_position.x - 1, 0)
            msg = MessageGetYList(app.block_position)
            app.send(left_origin_url, msg)
            log.info("sync_y_list-end")
