"""
"""
__author__ = "martin@amivono.com, daniel@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin@amivono.com, daniel@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from oan.util.decorator.accept import IGNORE, accepts, returns
from cube_node import OANCubeNode

class BlockList:
    '''
    All blocks in either x, y or the z direction.

    Each block contains x number of slots.

    '''
    # List of blocks where each block holds many slots.
    _blocks = None

    # Index of all CubeNodes with oan_id key.
    _nodes = None

    # Number of blocks the block list will expand with.
    EXPAND_SIZE = 1

    def __init__(self):
        self._blocks = []

    @accepts(IGNORE, int)
    def clear_block(self, block_pos):
        del self._blocks[block_pos][:]

    @accepts(IGNORE, int)
    @returns(bool)
    def has_block(self, block_pos):
        return block_pos <= self.size()-1

    @accepts(IGNORE, int, int)
    @returns(bool)
    def has_slot(self, block_pos, slot_pos):
        if self.has_block(block_pos) and slot_pos <= len(self._blocks[block_pos])-1:
            assert self._blocks[block_pos][slot_pos].__class__ == OANCubeNode
            return True
        else:
            return False

    @accepts(IGNORE)
    @returns(int)
    def size(self):
        return len(self._blocks)

    @accepts(IGNORE, int)
    @returns(int)
    def block_size(self, block_pos):
        if self.has_block(block_pos):
            return len(self._blocks[block_pos])
        else:
            return 0

    @accepts(IGNORE, int)
    @returns(list)
    def get_block(self, block_pos):
        return self._blocks[block_pos]

    @accepts(IGNORE, int, int)
    @returns(OANCubeNode)
    def get_slot(self, block_pos, slot_pos):
        return self.get_block(block_pos)[slot_pos]

    @accepts(IGNORE, int)
    def add_block(self, block):
        self._expand_size(self.size())
        self._block[self.size()].extend(block)

    @accepts(IGNORE, int, OANCubeNode)
    def add_slot(self, block_pos, cube_node):
        self._expand_size(block_pos)
        self._blocks[block_pos].append(cube_node)

    @accepts(IGNORE, int, list)
    def set_block(self, block_pos, block):
        self._expand_size(block_pos)
        self._blocks[block_pos] = block

    @accepts(IGNORE, int, int, OANCubeNode)
    @returns(bool)
    def _set_slot(self, block_pos, slot_pos, cube_node):
        if self.has_slot(block_pos, slot_pos):
            if self.get_slot(block_pos, slot_pos).oan_id == cube_node.oan_id:
                return False
            else:
                # TODO: We need to handle this in the big asyncron net.
                raise Exception("Slot is occupied with another cube node.")
        else:
            self._expand_slot_size(block_pos, slot_pos)
            self._blocks[block_pos][slot_pos] = cube_node
            return True

    @accepts(IGNORE, IGNORE)
    @returns(bool)
    def merge_block_list(self, block_list):
        changed = False
        block_pos=0
        for block in block_list._blocks:
            if self.merge_block(block_pos, block):
                changed = True
            block_pos+=1
        return changed

    @accepts(IGNORE, int, list)
    @returns(bool)
    def merge_block(self, block_pos, block):
        changed = False
        slot_pos = 0
        for slot in block:
            if self._set_slot(block_pos, slot_pos, slot):
                changed = True
            slot_pos+=1
        return changed

    @accepts(IGNORE, int)
    def _expand_size(self, block_pos):
        if block_pos+1 > len(self._blocks):
            for dummy in xrange(self.size(), block_pos + BlockList.EXPAND_SIZE):
                self._blocks.append([])

    @accepts(IGNORE, int, int)
    def _expand_slot_size(self, block_pos, slot_pos):
        self._expand_size(block_pos)
        if slot_pos+1 > self.block_size(block_pos):
            for dummy in xrange(self.block_size(block_pos), slot_pos + 1):
                self._blocks[block_pos].append(None)



from test.test_case import OANCubeTestCase


class TestBlockList(OANCubeTestCase):
    def test_block_list(self):
        block_list = BlockList()
        block_list.add_slot(2, OANCubeNode(self.create_oan_id(2)))
        self.assertEqual(block_list.block_size(2), 1)
        self.assertEqual(block_list.size(), 3)

        block_list.add_slot(1, OANCubeNode(self.create_oan_id(1)))
        self.assertEqual(block_list.block_size(1), 1)
        self.assertEqual(block_list.size(), 3)

        block_list.add_slot(3, OANCubeNode(self.create_oan_id(3)))
        self.assertEqual(block_list.block_size(3), 1)
        self.assertEqual(block_list.size(), 4)

        block_list.add_slot(0, OANCubeNode(self.create_oan_id(0)))
        block_list.add_slot(2, OANCubeNode(self.create_oan_id(102)))

        self.assert_block([block_list.get_slot(2, 0)], ['002'])
        self.assert_block([block_list.get_slot(2, 1)], ['102'])

        self.assert_block(block_list.get_block(2), ['002', '102'])

        self.assert_block(block_list.get_block(0), ['000'])
        self.assert_block(block_list.get_block(1), ['001'])
        self.assert_block(block_list.get_block(3), ['003'])

        block_list.clear_block(2)
        self.assert_block(block_list.get_block(2), [])

        block_list.merge_block(2, [OANCubeNode(self.create_oan_id(202))])
        self.assert_block(block_list.get_block(2), ['202'])

        # Complete list test.
        self.assert_block(block_list.get_block(0), ['000'])
        self.assert_block(block_list.get_block(1), ['001'])
        self.assert_block(block_list.get_block(2), ['202'])
        self.assert_block(block_list.get_block(3), ['003'])
