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

from block_position import BlockPosition
from cube_view import CubeView


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
        return self._cube_view.get_slot_pos(self.bind_url)

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
                    if not block_list.empty_slot(0, self.get_slot_pos()):
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
