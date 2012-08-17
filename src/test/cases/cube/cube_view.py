"""
"""
__author__ = "martin@amivono.com, daniel@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin@amivono.com, daniel@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"


from test.test_case import OANTestCase

from block_list import BlockList
from block_position import BlockPosition


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
