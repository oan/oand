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
    complete_list_x = None
    complete_list_y = None
    complete_list_z = None

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
            self.complete_list_x = True
        else:
            self.cube_view.x.merge_block(x_pos, app.cube_view.y.get(y_pos))
            self.complete_list_x = False

        if x_pos == app.block_position.x:
            self.cube_view.y.merge_block_list(app.cube_view.y)
            self.complete_list_y = True
        else:
            self.cube_view.y.merge_block(y_pos, app.cube_view.x.get(x_pos))
            self.complete_list_y = False

        # TODO Z

    def execute(self, app):
        log.info("%s got block position: %s" % (app.bind_url, self.block_position.id()))
        log.info("%s got cubeview.x: %s" % (app.bind_url, self.cube_view.x.get_blocks()))
        log.info("%s got cubeview.y: %s" % (app.bind_url, self.cube_view.y.get_blocks()))
        app.set_block_position(self.block_position)
        app.cube_view.set_cube_view(self.cube_view)
        log.info("%s has cubeview.x: %s" % (app.bind_url, app.cube_view.x.get_blocks()))
        log.info("%s has cubeview.y: %s" % (app.bind_url, app.cube_view.y.get_blocks()))

        #todo self.sync_x_list(app)
        self.sync_y_list(app)

        app.connect()

        app.push(app.network_builder.get_x(), MessageGiveBlockListX(app.cube_view.x))
        app.push(app.network_builder.get_y(), MessageGiveBlockListY(app.cube_view.y))
        app.push(app.network_builder.get_z(), MessageGiveBlockListZ(app.cube_view.z))

        app.push(app.network_builder.get_block(), MessageGiveBlockListX(app.cube_view.x))
        app.push(app.network_builder.get_block(), MessageGiveBlockListY(app.cube_view.y))
        app.push(app.network_builder.get_block(), MessageGiveBlockListZ(app.cube_view.z))

    def get_slot_neighbours_url(self, app):
        """
        Check if their is more occupied slots in the same block where I exist.

        """
        if len(app.cube_view.b) > 1:
            for node in app.cube_view.b:
                if app.bind_url != node.url:
                    return node.url
        return None

    def sync_y_list(self, app):
        log.info("whats in y %s %s" % (app.cube_view.y.get_blocks(), app.block_position.y))
        if not self.complete_list_y and app.block_position.y != 0:
            log.info("sync_y_list-begin")
            # TODO handle if left block is empty.

            # Send to same block
            destination_url = self.get_slot_neighbours_url(app)

            # Send to left block if we have no slot neighbour
            if not destination_url:
                if app.cube_view.x.has_slot(app.block_position.x - 1, 0):
                    destination_url = app.cube_view.x.get(app.block_position.x - 1, 0).url
                else:
                    raise Exception("sync-y-list left block don't exist.")

            msg = MessageGetYList(app.block_position)
            app.send(destination_url, msg)
            log.info("sync_y_list-end")
        else:
            log.info("no sync_y_list performed")
