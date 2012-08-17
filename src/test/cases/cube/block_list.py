"""
"""
__author__ = "martin@amivono.com, daniel@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin@amivono.com, daniel@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from test.test_case import OANTestCase


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
