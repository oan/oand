#!/usr/bin/env python
"""
A replacement and inheritence of unittest.TestCase

Add functionality to the existing TestCase class.

"""

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

    # Todo: Fix it
    # def run(self, result=None):
    #     """
    #     This is almost the same code as in the base class. The difference is the
    #     handling of tearDown, that will be executed when a KeyboardInterrupt
    #     exception is raised.

    #     """
    #     try:
    #         unittest.TestCase.run(self, result)
    #     except KeyboardInterrupt:
    #         print "KeyboardInterrupt"

    def wait(self, condition, timeout = 5):
        """
        Wait until the function given by condition returns True.

        condition
            Function that will be executed until it returns true.

        timeout
            Number of seconds to wait until timeout and return False.

        return
            True if condtion was met.

        """
        endtime = time() + timeout
        result = False
        while (endtime > time()):
            result = condition()
            if result:
                break
            sleep(0.1)

        return result

    def assertTrueWait(self, condition, timeout = 5):
        """
        Wait until the function given by condtion returns True.

        timeout
            Number of seconds to wait until timeout and return False.

        Example:
            self.assertTrueWait(lambda : 'n2' in node_list)

        """
        self.assertTrue(self.wait(condition, timeout))
