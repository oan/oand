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

class OANTestCase(unittest.TestCase):

    def run(self, result=None):
        '''
        This is almost the same code as in the base class. The difference is the
        handling of tearDown, that will be executed when a KeyboardInterrupt
        exception is raised.

        '''
        if result is None: result = self.defaultTestResult()
        result.startTest(self)
        testMethod = getattr(self, self._testMethodName)
        try:
            try:
                self.setUp()
            except KeyboardInterrupt:
                print "KeyboardInterrupt"
            except:
                result.addError(self, self._exc_info())
                return

            ok = False
            try:
                testMethod()
                ok = True
            except self.failureException:
                result.addFailure(self, self._exc_info())
            except KeyboardInterrupt:
                print "KeyboardInterrupt"
            except:
                result.addError(self, self._exc_info())

        finally:
            try:
                self.tearDown()
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self._exc_info())
                ok = False
            if ok: result.addSuccess(self)
            result.stopTest(self)
