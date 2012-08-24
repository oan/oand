"""
"""
__author__ = "martin@amivono.com, daniel@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin@amivono.com, daniel@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"


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

    def get_slot_pos(self, bind_url):
        i = 0
        for node in self.b:
            if node.url == bind_url:
                return i
            i += 1

        raise Exception("Key %s not found." % (bind_url,))

    def _clear(self):
        # Share the same block where each direction intersect/meet.
        self.b = []

        self.x = BlockList()
        self.x.set_shared_block(self.block_position.x, self.b)

        self.y = BlockList()
        self.y.set_shared_block(self.block_position.y, self.b)

        self.z = BlockList()
        self.z.set_shared_block(self.block_position.z, self.b)


from test.test_case import OANCubeTestCase
from cube_node import OANCubeNode


class TestCubeView(OANCubeTestCase):
    def test_cube_view_block_pos_0(self):
        cube_view = CubeView(BlockPosition())
        cube_view.b.append(OANCubeNode(self.create_oan_id(0)))
        self.assert_block(cube_view.b, ['000'])

        cube_view.x.add(0, OANCubeNode(self.create_oan_id(1)))
        self.assert_block(cube_view.x.get(0), ["000", "001"])

        cube_view.y.add(0, OANCubeNode(self.create_oan_id(2)))
        self.assert_block(cube_view.y.get(0), ["000", "001", "002"])

        cube_view.z.add(0, OANCubeNode(self.create_oan_id(3)))
        self.assert_block(cube_view.z.get(0), ["000", "001", "002", "003"])

        # Total cube view
        self.assert_block(cube_view.b, ["000", "001", "002", "003"])
        self.assert_block(cube_view.x.get(0), ["000", "001", "002", "003"])
        self.assert_block(cube_view.y.get(0), ["000", "001", "002", "003"])
        self.assert_block(cube_view.z.get(0), ["000", "001", "002", "003"])
