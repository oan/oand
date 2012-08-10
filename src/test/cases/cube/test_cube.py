#!/usr/bin/env python
"""
Test cases for oan.cube

OAN Cube Rules
* All nodes will push their node lists to their bffs every hour.
  So all nodes can see if any node has expired, and a slot is free.
* When a new node should be assigned a slot, an empty slot is primary taken
  and if none are free an expired slot will be assigned.
* All new slots are choosen from the lowest possible x, y, z coordinate.
* If more then x nodes exist in the same slot, the node with the highest
  node_id (uuid) has to move.

"""

__author__ = "martin@amivono.com, daniel@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin@amivono.com, daniel@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import time

from test.test_case import OANTestCase
from oan.util import log

# Max slots in block
MAX_SLOTS_IN_BLOCK = 4


class Message(object):
    """Base class for all Messages."""

    """
    The bind url for the node that sends the message.

    """
    origin_url = None


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
        if self.empty_list(app, app.cube_view.y) and app.block_position.y != 0:
            log.info("sync_y_list")
            # TODO handle if left block is empty.
            left_origin_url = app.cube_view.x.get(app.block_position.x - 1, 0)
            msg = MessageGetYList(app.block_position)
            app.send(left_origin_url, msg)


class MessageGetYList(Message):
    pos = None

    def __init__(self, block_position):
        self.origin_position = block_position

    def is_in_block_with_y_list(self, app):
        return (
            app.block_position.y < self.origin_position.y and
            app.block_position.x == self.origin_position.x
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
        log.info("MessageGetYList step 3 to %s" % self.origin_url)
        log.info
        app.send(self.origin_url, MessageGiveBlockListY( app.cube_view.y))

    def redirects_to_right_in_cube(self, app):
        log.info("MessageGetYList step 2 to %s" % app.cube_view.x.size(self.origin_position.x))
        msg = MessageRedirect(app.cube_view.x.get(self.origin_position.x, 0), self)
        app.send(self.origin_url, msg)

    def redirects_up_in_cube(self, app):
        destination_url = None
        for y_pos in reversed(xrange(app.block_position.y)):
            log.info("y_pos %s" % y_pos)
            if app.cube_view.y.has_slot(y_pos, 0):
                destination_url = app.cube_view.y.get_slot(y_pos, 0)
                log.info("hit 1")
                break

        if not destination_url:
            for x_pos in reversed(xrange(app.block_position.x)):
                log.info("x_pos %s" % x_pos)
                if app.cube_view.x.has_slot(x_pos, 0):
                    destination_url = app.block_position.x.get(x_pos, 0)
                    log.info("hit 2")
                    break

        log.info("MessageGetYList step 1 to %s" % destination_url)
        if destination_url:
            msg = MessageRedirect(destination_url, self)
            app.send(self.origin_url, msg)

    def execute(self, app):
        log.info("MessageGetYList slot:%s x:%s y:%s x_pos %s of %s y_pos %s of %s" % (
                 app.bind_url,
                 app.block_position.x, app.block_position.y,
                 self.origin_position.x, app.cube_view.x.size(),
                 self.origin_position.y, app.cube_view.y.size()
        ))
        log.info(app.cube_view.x.get_blocks())
        log.info(app.cube_view.y.get_blocks())

        if self.is_in_block_with_y_list(app):
            self.forwards_y_list_back_to_origin(app)

        elif self.is_in_block_who_knows_block_with_y_list(app):
            self.redirects_to_right_in_cube(app)

        elif self.is_in_block_left_of_origin(app):
            self.redirects_up_in_cube(app)

class MessageRedirect(Message):
    bind_url = None
    message = None
    def __init__(self, bind_url, message):
        self.bind_url = bind_url
        self.message = message
        log.info("Redirect %s to %s" % (
                 self.message.__class__.__name__, self.bind_url))

    def execute(self, app):
        app.send(self.bind_url, self.message)


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
            OANLogCounter.begin("GiveBlockListX Forward ")
            app.push(app.network_builder.get_x(), self)
            OANLogCounter.end("GiveBlockListX Forward ")
        else:
            OANLogCounter.hit("GiveBlockListX Not needed")


class MessageGiveBlockListY(MessageGiveBlockList):
    def execute(self, app):
        log.info("On %s Merge list Y" % (app.bind_url))
        if app.cube_view.y.merge_block_list(self.block_list):
            OANLogCounter.begin("GiveBlockListY Forward")
            app.push(app.network_builder.get_y(), self)
            OANLogCounter.end("GiveBlockListY Forward")
        else:
            OANLogCounter.hit("GiveBlockListY Not needed")


class MessageGiveBlockListZ(MessageGiveBlockList):
    def execute(self, app):
        log.info("On %s Merge list Z" % (app.bind_url))
        if app.cube_view.z.merge_block_list(self.block_list):
            OANLogCounter.begin("GiveBlockListZ Forward")
            app.push(app.network_builder.get_z(), self)
            OANLogCounter.end("GiveBlockListZ Forward")
        else:
            OANLogCounter.hit("GiveBlockListZ Not needed")


class MessageGetSlotNode(): pass
class MessagePing(): pass
class MessageHeartbeat(): pass
class MessageGetValue(): pass
class MessageSetValue(): pass


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


class BlockPosition:
    """
    The position of a block in the cube.

    """
    x = None
    y = None
    z = None

    def __init__(self, x = 0 , y = 0 , z = 0):
        self.x = x
        self.y = y
        self.z = z

    def id(self):
        return (self.x, self.y ,self.z)


class TestBlockPosition(OANTestCase):
    def dis_test_block_position(self):
        pos = BlockPosition(10, 11, 12)
        self.assertEqual(pos.id(), (10, 11, 12))
        self.assertEqual(pos.x, 10)
        self.assertEqual(pos.y, 11)
        self.assertEqual(pos.z, 12)


class BlockList:
    '''
    All blocks in either x, y or the z direction.

    Each block contains x number of slots.

    '''
    # List of blocks where each block holds many slots.
    _blocks = None

    # Number of blocks the block list will expand with.
    EXPAND_SIZE = 1

    def __init__(self):
        self._clear()

    def _clear(self):
        self._blocks = []

    def clear_block(self, block_pos):
        del self.get(block_pos)[:]

    def add(self, block_pos, url):
        # TODO rename add_slot
        self.get_block(block_pos).append(url)

        return self.block_size(block_pos)-1

    def add_block(self, block):
        self.get(self.size()).extend(block)

    def merge_block_list(self, block_list):
        changed = False
        pos=0
        for block in block_list.get_blocks():
            if self.merge_block(pos, block):
                changed = True
            pos+=1
        return changed

    def merge_block(self, block_pos, block):
        self._expand_size(block_pos)

        changed = False
        slot_pos = 0
        for slot in block:
            if self.set_slot(block_pos, slot_pos, slot):
                changed = True
            slot_pos+=1
        return changed

    def get(self, block_pos, slot_pos = None):
        if slot_pos == None:
            return self.get_block(block_pos)
        else:
            return self.get_slot(block_pos, slot_pos)

    def get_blocks(self):
        return self._blocks

    def get_block(self, block_pos):
        # TODO: remove expand_size from all gets, should raise Exception if
        #       not exist.
        self._expand_size(block_pos)
        return self._blocks[block_pos]

    def get_slot(self, block_pos, slot_pos):
        return self.get_block(block_pos)[slot_pos]

    def empty_slot(self, block_pos, slot_pos):
        if (len(self._blocks) > block_pos and
            len(self._blocks[block_pos]) > slot_pos):
            return False
        return True

    def remove(self, block_pos, url):
        self._blocks[block_pos].remove(url)

    def set(self, block_pos, block):
        return self.merge_block(block_pos, block)

    def set_slot(self, block_pos, slot_pos, url):
        self._expand_slot_size(block_pos, slot_pos)
        if self._blocks[block_pos][slot_pos] == url:
            return False
        else:
            self._blocks[block_pos][slot_pos] = url
            return True


    def set_shared_block(self, block_pos, block):
        self._expand_size(block_pos)
        self._blocks[block_pos] = block

    def _expand_size(self, block_pos):
        if block_pos+1 > len(self._blocks):
            for dummy in xrange(self.size(), block_pos + BlockList.EXPAND_SIZE):
                self._blocks.append([])

    def _expand_slot_size(self, block_pos, slot_pos):
        self._expand_size(block_pos)
        if slot_pos+1 > self.block_size(block_pos):
            for dummy in xrange(self.block_size(block_pos), slot_pos + 1):
                self._blocks[block_pos].append(None)

    def _has_block(self, block_pos):
        return block_pos <= self._size()-1

    def has_slot(self, block_pos, slot_pos):
        return self._has_block(block_pos) and slot_pos <= len(self._blocks[block_pos])-1

    def _size(self):
        # TODO should replace size
        return len(self._blocks)

    def block_size(self, block_pos):
        if self._has_block(block_pos):
            return len(self.get(block_pos))
        else:
            return 0

    def size(self, block_pos = None):
        if block_pos == None:
            return self._size()
        else:
            return self.block_size(block_pos)


class TestBlockList(OANTestCase):
    def dis_test_block_list(self):
        block_list = BlockList()
        self.assertEqual(block_list.add(2, "002"), 0)
        self.assertEqual(block_list.size(2), 1)
        self.assertEqual(block_list.size(), 3)

        self.assertEqual(block_list.add(1, "001"), 0)
        self.assertEqual(block_list.size(1), 1)
        self.assertEqual(block_list.size(), 3)

        self.assertEqual(block_list.add(3, "003"), 0)
        self.assertEqual(block_list.size(3), 1)
        self.assertEqual(block_list.size(), 4)

        self.assertEqual(block_list.add(0, "000"), 0)
        self.assertEqual(block_list.add(2, "002B"), 1)

        self.assertEqual(block_list.get(2, 0), "002")
        self.assertEqual(block_list.get(2, 1), "002B")
        self.assertEqual(block_list.get(2), ["002", "002B"])
        self.assertEqual(block_list.get(0), ["000"])
        self.assertEqual(block_list.get(1), ["001"])
        self.assertEqual(block_list.get(3), ["003"])

        block_list.remove(2, "002")
        self.assertEqual(block_list.get(2), ["002B"])

        block_list.clear_block(2)
        self.assertEqual(block_list.get(2), [])

        block_list.set(2, ["002C"])
        self.assertEqual(block_list.get(2), ["002C"])

        # Complete list test.
        self.assertEqual(block_list.get(0), ["000"])
        self.assertEqual(block_list.get(1), ["001"])
        self.assertEqual(block_list.get(2), ["002C"])
        self.assertEqual(block_list.get(3), ["003"])


class CubeView:
    """
    List of blocks in x, y, z direction.

    """
    block_position = None
    b = None
    x = None
    y = None
    z = None

    def __init__(self, block_position = None):
        if block_position:
            self.set_block_position(block_position)
        else:
            self.set_block_position(BlockPosition(0, 0, 0))

    def set_block_position(self, block_position):
        self.block_position = block_position
        self._clear()

    def set_cube_view(self, cube_view):
        self._clear()

        self.x.merge_block_list(cube_view.x)
        self.y.merge_block_list(cube_view.y)
        self.z.merge_block_list(cube_view.z)

    def _clear(self):
        # Share the same block where each direction intersect/meet.
        self.b = []

        self.x = BlockList()
        self.x.set_shared_block(self.block_position.x, self.b)

        self.y = BlockList()
        self.y.set_shared_block(self.block_position.y, self.b)

        self.z = BlockList()
        self.z.set_shared_block(self.block_position.z, self.b)

class TestCubeView(OANTestCase):
    def dis_test_cube_view_block_pos_0(self):
        cube_view = CubeView(BlockPosition())
        cube_view.b.append("000")
        self.assertEqual(cube_view.b, ["000"])

        cube_view.x.add(0, "001")
        self.assertEqual(cube_view.x.get(0), ["000", "001"])

        cube_view.y.add(0, "002")
        self.assertEqual(cube_view.y.get(0), ["000", "001", "002"])

        cube_view.z.add(0, "003")
        self.assertEqual(cube_view.z.get(0), ["000", "001", "002", "003"])

        # Total cube view
        self.assertEqual(cube_view.b, ["000", "001", "002", "003"])
        self.assertEqual(cube_view.x.get(0), ["000", "001", "002", "003"])
        self.assertEqual(cube_view.y.get(0), ["000", "001", "002", "003"])
        self.assertEqual(cube_view.z.get(0), ["000", "001", "002", "003"])

    # TODO
    # def dis_test_cube_view_block_pos_2(self):
    #     cube_view = CubeView(BlockPosition())
    #     cube_view.set_block_pos(2, 2, 2)
    #     cube_view.b.append("000")
    #     self.assertEqual(cube_view.b, ["000"])


class NetworkBuilder:
    bind_url = None
    block_pos = None

    block = None

    previous_x = None
    next_x = None
    faraway_x = None

    previous_y = None
    next_y = None
    faraway_y = None

    previous_z = None
    next_z = None
    faraway_z = None

    # The cube view build is working with.
    _cube_view = None

    def __init__(self, bind_url, block_pos):
        self.bind_url = bind_url
        self.block_pos = block_pos
        self._clear()

    def get_block(self):
        return self.block

    def get_x(self):
        return self.previous_x + self.next_x + self.faraway_x

    def get_y(self):
        return self.previous_y + self.next_y + self.faraway_y

    def get_z(self):
        return self.previous_z + self.next_z + self.faraway_z

    def get_all(self):
        urls = (self.get_block() + self.get_x() + self.get_y() + self.get_z())
        return set(urls)

    def get_slot_pos(self):
        return self._cube_view.b.index(self.bind_url)

    def build(self, cube_view):
        """
        Build a network view of urls in b, x, y, z direction.

        * Each node will communicate with all other nodes in the same block.
        * Each node will communicate with one slot/node in the the nearest
          block forward and backward in x, y and z direction.
        * Each node will communicate with one slot/node in a block that is
          faraway x, y and z direction. Faraway is rougly defined as
          x_pos + (max_x_size/2).

        * TODO:
          When a node connects to another block, it will connect to the node
          with the same slot postion as the connection node. If that slot
          doesn't exist, the highest slot id will be used.

        """
        log.info("%s build network." % self.bind_url)
        self._cube_view = cube_view
        self._clear()
        self._add_current_block(cube_view)

        self._add_previous_block(self.block_pos.x, cube_view.x, self.previous_x)
        self._add_next_block(self.block_pos.x, cube_view.x, self.next_x)
        self._add_faraway_block(self.block_pos.x, cube_view.x, self.faraway_x)

        self._add_previous_block(self.block_pos.y, cube_view.y, self.previous_y)
        self._add_next_block(self.block_pos.y, cube_view.y, self.next_y)
        self._add_faraway_block(self.block_pos.y, cube_view.y, self.faraway_y)

        self._add_previous_block(self.block_pos.z, cube_view.z, self.previous_z)
        self._add_next_block(self.block_pos.z, cube_view.z, self.next_z)
        self._add_faraway_block(self.block_pos.z, cube_view.z, self.faraway_z)

    def _clear(self):
        self.block = []

        self.previous_x = []
        self.next_x = []
        self.faraway_x = []

        self.previous_y = []
        self.next_y = []
        self.faraway_y = []

        self.previous_z = []
        self.next_z = []
        self.faraway_z = []

    def _add_current_block(self, cube_view):
        """Connect to all nodes in current block."""
        for bind_url in cube_view.b:
            self._add_url(bind_url, self.block)


    def _add_previous_block(self, block_pos_cord, block_list, urls):
        """Connect to the previous block, the block before current block."""
        if block_list.size() > 1:
            # If current block is the first block, connect to last block,
            if block_pos_cord == 0:
                # But not if the current block is the last block
                last_block_cord = block_list.size()-1
                if block_pos_cord != last_block_cord:
                    if not block_list.empty_slot(last_block_cord, self.get_slot_pos()):
                        self._add_url(block_list.get(last_block_cord, self.get_slot_pos()), urls)

            # Connect to previous node if it exists.
            elif block_pos_cord - 1 >= 0:
                if block_list.has_slot(block_pos_cord - 1, self.get_slot_pos()):
                    self._add_url(block_list.get_slot(block_pos_cord - 1, self.get_slot_pos()), urls)

            else:
                raise Exception('Invalid block_pos_cord: %s' % block_pos_cord)

    def _add_next_block(self, block_pos_cord, block_list, urls):
        """Connect to the next block, the block after current block."""
        if block_list.size() > 1:
            # If current block is the last block, connect to first block,
            last_block_cord = block_list.size()-1
            if block_pos_cord == last_block_cord:
                if block_list.size() > 2:
                    self._add_url(block_list.get(0, self.get_slot_pos()), urls)

            # Connect to next node if it exists.
            elif block_pos_cord + 1 <= block_list.size()-1:
                if not block_list.empty_slot(block_pos_cord + 1, self.get_slot_pos()):
                    self._add_url(block_list.get(block_pos_cord + 1, self.get_slot_pos()), urls)

            else:
                raise Exception('Invalid block_pos_cord: %s' % block_pos_cord)

    def _add_faraway_block(self, block_pos_cord, block_list, urls):
        """
        Connect to a faraway block.

        Faraway blocks are only used when a list has more than X blocks.

        TODO: Add constant for minimum number of faraway blocks. Update
              unit tests. And increase the value to < 10
        """
        if block_list.size() > 2:
            block_list_middle_cord = int(block_list.size()/2)
            faraway_block_pos_cord = block_pos_cord + block_list_middle_cord

            if faraway_block_pos_cord >= block_list.size()-1:
                faraway_block_pos_cord -= block_list.size()

            if not block_list.empty_slot(faraway_block_pos_cord, self.get_slot_pos()):
                self._add_url(block_list.get(faraway_block_pos_cord, self.get_slot_pos()), urls)

    def _add_url(self, url, urls):
        if url and url != self.bind_url and url not in urls:
            log.info("%s added %s to network." % (self.bind_url, url))
            urls.append(url)


class TestNetworkBuilder(OANTestCase):
    def dis_test_connect(self):
        cube_view = CubeView(BlockPosition(0, 0, 0))
        cube_view.b.append("001")
        cube_view.b.append("002")
        cube_view.b.append("003")
        cube_view.b.append("004")

        bff = NetworkBuilder("002", BlockPosition(0, 0, 0))
        bff.build(cube_view)
        self.assertEqual(bff.block, ["001", "003", "004"])

        cube_view.b.append("005")
        bff.build(cube_view)
        self.assertEqual(bff.block, ["001", "003", "004", "005"])

        cube_view.b.remove("003")
        bff.build(cube_view)
        self.assertEqual(bff.block, ["001", "004", "005"])

        self.assertEqual(bff.get_all(), set(["001", "004", "005"]))

    def get_cube_view(self, block_pos):
        cube_view = CubeView(block_pos)
        cube_view.x.add(0, "000")
        cube_view.x.add(1, "001")
        cube_view.x.add(2, "002")
        cube_view.x.add(3, "003")
        cube_view.x.add(4, "004")

        cube_view.y.add(0, "100")
        cube_view.y.add(1, "101")
        cube_view.y.add(2, "102")
        cube_view.y.add(3, "103")
        cube_view.y.add(4, "104")

        cube_view.z.add(0, "200")
        cube_view.z.add(1, "201")
        cube_view.z.add(2, "202")
        cube_view.z.add(3, "203")
        cube_view.z.add(4, "204")

        return cube_view

    def dis_test_build_from_first_node(self):
        block_pos = BlockPosition(0, 0, 0)
        cube_view = self.get_cube_view(block_pos)
        bff = NetworkBuilder("000", block_pos)
        bff.build(cube_view)

        self.assertEqual(bff.previous_x, ["004"])
        self.assertEqual(bff.next_x, ["001"])
        self.assertEqual(bff.faraway_x, ["002"])

        self.assertEqual(bff.previous_y, ["104"])
        self.assertEqual(bff.next_y, ["101"])
        self.assertEqual(bff.faraway_y, ["102"])

        self.assertEqual(bff.previous_z, ["204"])
        self.assertEqual(bff.next_z, ["201"])
        self.assertEqual(bff.faraway_z, ["202"])

        self.assertEqual(bff.get_all(), set(['201', '200', '202', '204', '002', '001', '004', '102', '100', '101', '104']))

    def dis_test_build_from_middle_node(self):
        block_pos = BlockPosition(2, 2, 2)

        cube_view = self.get_cube_view(block_pos)
        bff = NetworkBuilder("002", block_pos)
        bff.build(cube_view)

        self.assertEqual(bff.previous_x, ["001"])
        self.assertEqual(bff.next_x, ["003"])
        self.assertEqual(bff.faraway_x, ["004"])

        self.assertEqual(bff.previous_y, ["101"])
        self.assertEqual(bff.next_y, ["103"])
        self.assertEqual(bff.faraway_y, ["104"])

        self.assertEqual(bff.previous_z, ["201"])
        self.assertEqual(bff.next_z, ["203"])
        self.assertEqual(bff.faraway_z, ["204"])

        self.assertEqual(bff.get_all(), set(['201', '203', '202', '204', '003', '001', '004', '102', '103', '101', '104']))

    def dis_test_build_from_last_node(self):
        block_pos = BlockPosition(4, 4, 4)

        cube_view = self.get_cube_view(block_pos)
        bff = NetworkBuilder("004", block_pos)
        bff.build(cube_view)

        self.assertEqual(bff.previous_x, ["003"])
        self.assertEqual(bff.next_x, ["000"])
        self.assertEqual(bff.faraway_x, ["001"])

        self.assertEqual(bff.previous_y, ["103"])
        self.assertEqual(bff.next_y, ["100"])
        self.assertEqual(bff.faraway_y, ["101"])

        self.assertEqual(bff.previous_z, ["203"])
        self.assertEqual(bff.next_z, ["200"])
        self.assertEqual(bff.faraway_z, ["201"])

        self.assertEqual(bff.get_all(), set(['201', '200', '203', '204', '003', '001', '000', '103', '100', '101', '104']))


class OANLogCounter():

    class LogEntry():
        counter = None
        last_elapsed = None
        total_elapsed = None
        min_elapsed = None
        max_elapsed = None

        def __init__(self):
            self.counter = 0
            self.last_elapsed = 0
            self.total_elapsed = 0
            self.min_elapsed = None
            self.max_elapsed = 0

        def __str__(self):
            return ("counter:{0:>6}, total:{1:>7.4f}, avg:{2:>7.4f}, " +
                    "min:{3:>7.4f}, max:{4:>7.4f}").format(
                    self.counter, self.total_elapsed,
                    self.total_elapsed / (self.counter or 1),
                    self.min_elapsed, self.max_elapsed
            )

    _entries = {}

    @staticmethod
    def clear():
        OANLogCounter._entries = {}

    @staticmethod
    def begin(key):
        if key not in OANLogCounter._entries:
            entry = OANLogCounter.LogEntry()
            OANLogCounter._entries[key] = entry
        else:
            entry = OANLogCounter._entries[key]

        entry.start = time.time()

    @staticmethod
    def end(key):
        entry = OANLogCounter._entries[key]
        entry.counter += 1
        entry.last_elapsed = (time.time() - entry.start)
        entry.total_elapsed += entry.last_elapsed
        entry.max_elapsed = max(entry.last_elapsed, entry.max_elapsed)
        if entry.min_elapsed == None:
            entry.min_elapsed = entry.last_elapsed
        else:
            entry.min_elapsed = min(entry.last_elapsed, entry.min_elapsed)

    @staticmethod
    def hit(key):
        OANLogCounter.begin(key)
        OANLogCounter.end(key)

    @staticmethod
    def result():

        ret = ""
        keys = OANLogCounter._entries.keys()
        keys.sort()

        for key in keys:
            ret += "\n{0:<30} -> {1}".format(key, str(OANLogCounter._entries[key]))

        return ret



class TestOANLogCounter(OANTestCase):
    def test_counter(self):
        OANLogCounter.clear()
        self.assertEqual(OANLogCounter.result(), "")

        OANLogCounter.begin("test")
        OANLogCounter.end("test")

        self.assertEqual(OANLogCounter.result(), "\ntest                           -> counter:     1, total: 0.0000, avg: 0.0000, min: 0.0000, max: 0.0000")
        OANLogCounter.clear()


class NetworkCounter:
    """
    Statistics for things done by and to a node.

    receive        - received messages
    push           - pushed messages
    send           - sent messages
    disconnect     - disconnects from a remote NetworkView
    connect        - connects to a remote NetworkView
    accept         - accepts of incomming connections
    close          - closed connections.

    """
    receive = None
    push = None
    send = None
    connect = None
    disconnect = None
    accept = None
    close = None

    def __init__(self):
        self.receive = 0
        self.push = 0
        self.send = 0
        self.connect = 0
        self.disconnect = 0
        self.accept = 0
        self.close = 0

    def __str__(self):
        return ("receive:{0:>4}, push:{1:>4}, send:{2:>4}, " +
               "connect:{3:>4}, accept:{4:>4}, "+
               "disconnect:{5:>4}, close:{6:>4}").format(
                    self.receive, self.push, self.send,
                    self.connect, self.accept,
                    self.disconnect, self.close
                )

    def __iadd__(self, obj):
        if isinstance(obj, NetworkCounter):
            self.receive += obj.receive
            self.push += obj.push
            self.send += obj.send
            self.connect += obj.connect
            self.disconnect += obj.disconnect
            self.accept += obj.accept
            self.close += obj.close
            return self
        else:
            raise TypeError("Not a Counter object.")


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
        OANLogCounter.begin("%s send" % message.__class__.__name__)
        self.counter.send += 1
        log.info("%s sent %s to %s " % (self._bind_url, message.__class__.__name__, Connections.all[url]._bind_url))
        message.origin_url = self._bind_url
        if url not in self._sockets:
            self.connect([url])
            # TODO
            # self.disconnect_and_forget_if_not_used(url, "5 minutes")

        OANLogCounter.end("%s send" % message.__class__.__name__)
        self._sockets[url].receive(message)

    def push(self, urls, message):
        self.counter.push += 1
        for url in urls:
            self.send(url, message)

    def receive(self, message):
        log.info("%s received %s from %s " % (self._bind_url, message.__class__.__name__, message.origin_url))
        OANLogCounter.begin("%s received" % message.__class__.__name__)
        self.counter.receive += 1
        self.received_cb(self, message)
        OANLogCounter.end("%s received" % message.__class__.__name__)

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


class OANApplication:
    bind_url = None
    cube_view = None
    block_position = None
    network_builder = None
    network_view = None

    def __init__(self, bind_url):
        self.bind_url = bind_url

        self.cube_view = CubeView()
        self.network_view = NetworkView(self.bind_url)
        self.network_view.received_cb = self.received_cb

        self.set_block_position(BlockPosition(0, 0, 0))
        self.cube_view.b.append(self.bind_url)

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
        self.connect()


class TestOANCube(OANTestCase):
    _apps = None

    def trigger_5minute_cron(self):
        """
        Emulates a cron job that is executed every 5 minute.

        Naturally a unit test don't have any scheduler/cron, so this function
        should be called manually.

        """
        for app in self._apps.values():
            app.trigger_5minute_cron()

    def connect_node(self, url, block_id, test_list):
        log.info("======= %s =======================================================================================" % url)
        log.info("Create %s with block_id %s" % (url, block_id))

        app = OANApplication(url)
        self._apps[url] = app
        app.send('001', MessageConnect())

        self.trigger_5minute_cron()

        self.assertEqual(app.block_position.id(), block_id)

        x_max_size = max(3, self._apps['001'].cube_view.x.size())

        x_list = self.get_x_list(block_id, test_list, x_max_size)
        self.assertEqual(app.cube_view.x.get_blocks(), x_list)

        y_list = self.get_y_list(block_id, test_list, x_max_size)
        self.assertEqual(app.cube_view.y.get_blocks(), y_list)

    def get_x_list(self, slot_id, test_list, width):
        x, y, z = slot_id

        new_x_list = []
        for c_list in test_list[y*width:y*width+width]:
            new_c_list = []
            for node in c_list:
                if node != "___":
                    new_c_list.append(str(node))
            if len(new_c_list):
                new_x_list.append(new_c_list)
        log.info('Expected: x(%s) %s' % (slot_id, new_x_list))
        return new_x_list

    def get_y_list(self, slot_id, test_list, width):
        x, y, z = slot_id

        new_y_list = []
        for slot_pos in xrange(x, len(test_list), width):
            c_list = test_list[slot_pos]
            log.info("slot_id %s slot_pos %s %s" % (slot_id, slot_pos, c_list))
            new_c_list = []
            for node in c_list:
                if node != "___":
                    new_c_list.append(str(node))
            if len(new_c_list):
                new_y_list.append(new_c_list)
        log.info('Expected: y(%s) %s' % (slot_id, new_y_list))
        return new_y_list

    def test_connection(self):
        OANLogCounter.clear()
        self._apps = {}
        Connections.clear()

        first_app = OANApplication('001')
        self._apps['001'] = first_app
        self.assertEqual(first_app.block_position.id(), (0, 0, 0))

        self.connect_node("002", (0, 0, 0), [["001", "002", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("003", (0, 0, 0), [["001", "002", "003", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("004", (0, 0, 0), [["001", "002", "003", "004"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("005", (1, 0, 0), [["001", "002", "003", "004"], ["005", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("006", (1, 0, 0), [["001", "002", "003", "004"], ["005", "006", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("007", (1, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("008", (1, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("009", (2, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("010", (2, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("011", (2, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("012", (2, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("013", (0, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("014", (0, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("015", (0, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("016", (0, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("017", (1, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("018", (1, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("019", (1, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("020", (1, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("021", (2, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("022", (2, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("023", (2, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("024", (2, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("025", (0, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("026", (0, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("027", (0, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("028", (0, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("029", (1, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("030", (1, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("031", (1, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "___"], ["___", "___", "___", "___"]])

        self.connect_node("032", (1, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["___", "___", "___", "___"]])

        self.connect_node("033", (2, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "___", "___", "___"]])

        self.connect_node("034", (2, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "___", "___"]])

        self.connect_node("035", (2, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "___"]])

        self.connect_node("036", (2, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"]])

        self.connect_node("037", (0, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"],
                                             ["037", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("038", (0, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"],
                                             ["037", "038", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("039", (0, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"],
                                             ["037", "038", "039", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("040", (0, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])


        self.connect_node("041", (3, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "___", "___", "___"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["___", "___", "___", "___"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["___", "___", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("042", (3, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "___", "___"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["___", "___", "___", "___"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["___", "___", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("043", (3, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "___"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["___", "___", "___", "___"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["___", "___", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("044", (3, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["___", "___", "___", "___"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["___", "___", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("045", (3, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "___", "___", "___"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["___", "___", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("046", (3, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "___", "___"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["___", "___", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("047", (3, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "___"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["___", "___", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("048", (3, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["___", "___", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("049", (3, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "___", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("050", (3, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("051", (3, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("052", (3, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("053", (1, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("054", (1, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("055", (1, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("056", (1, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "056"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("057", (2, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "056"], ["057", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("058", (2, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "056"], ["057", "058", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("059", (2, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "056"], ["057", "058", "059", "___"], ["___", "___", "___", "___"]])

        self.connect_node("060", (2, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "056"], ["057", "058", "059", "060"], ["___", "___", "___", "___"]])

        self.connect_node("061", (3, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "056"], ["057", "058", "059", "060"], ["061", "___", "___", "___"]])

        self.connect_node("062", (3, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "056"], ["057", "058", "059", "060"], ["061", "062", "___", "___"]])

        self.connect_node("063", (3, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "056"], ["057", "058", "059", "060"], ["061", "062", "063", "___"]])

        self.connect_node("064", (3, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "056"], ["057", "058", "059", "060"], ["061", "062", "063", "064"]])


        # Disconnect all sockets
        for app in self._apps.values():
            app.network_view.disconnect()

        for app in self._apps.values():
            self.assertEqual(
                    app.network_view.counter.connect + app.network_view.counter.accept,
                    app.network_view.counter.disconnect + app.network_view.counter.close
                )


        #
        # DEBUG
        #
        keys = Connections.all.keys()
        keys.sort()

        log.info("=== Slot id =======================")
        for key in keys:
            network_view = Connections.all[key]
            app = self._apps[key]
            log.info("slot_id: %s %s" % (network_view._bind_url, app.block_position.id()))

        log.info("=== Network Counters ======================")
        counter_total = NetworkCounter()
        for key in keys:
            network_view = Connections.all[key]
            log.info("Counters: %s %s" % (network_view._bind_url, network_view.counter))
            counter_total += network_view.counter
        log.info("TOTAL           %s" % (counter_total))


        self.assertEqual(counter_total.receive, counter_total.send)
        self.assertEqual(
                counter_total.connect + counter_total.accept,
                counter_total.disconnect + counter_total.close
            )

        log.info("=== Timers ======================")
        log.info(OANLogCounter.result())

