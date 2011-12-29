#!/usr/bin/env python
'''
A replacement of unittest.TestCase

This is almost the same code as in the base class. The difference is the
handling of tearDown, that will be executed when a KeyboardInterrupt exception
is raised.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import sys
import unittest
from time import time, sleep

class OANTestCase(unittest.TestCase):

    def run(self, result=None):
        '''
        This is almost the same code as in the base class. The difference is the
        handling of tearDown, that will be executed when a KeyboardInterrupt
        exception is raised.

        I remove the code it doesnt work with python 2.7

        '''
        try:
            unittest.TestCase.run(self, result)
        except KeyboardInterrupt:
            print "KeyboardInterrupt"
