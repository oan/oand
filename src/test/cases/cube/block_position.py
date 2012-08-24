"""
"""
__author__ = "martin@amivono.com, daniel@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin@amivono.com, daniel@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from test.test_case import OANTestCase


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
    def test_block_position(self):
        pos = BlockPosition(10, 11, 12)
        self.assertEqual(pos.id(), (10, 11, 12))
        self.assertEqual(pos.x, 10)
        self.assertEqual(pos.y, 11)
        self.assertEqual(pos.z, 12)
