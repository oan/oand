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

import unittest

class OANTestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        '''
        This is an exact copy of the unittest.TestCase.__init__.

        It was needed to get the self.__testMethodName to work in run().

        '''
        try:
            self.__testMethodName = methodName
            testMethod = getattr(self, methodName)
            self.__testMethodDoc = testMethod.__doc__
        except AttributeError:
            raise ValueError, "no such test method in %s: %s" % \
                  (self.__class__, methodName)

    def run(self, result=None):
        '''
        This is almost the same code as in the base class. The difference is the
        handling of tearDown, that will be executed when a KeyboardInterrupt
        exception is raised.

        '''
        if result is None: result = self.defaultTestResult()
        result.startTest(self)
        testMethod = getattr(self, self.__testMethodName)
        try:
            try:
                self.setUp()
            except KeyboardInterrupt:
                print "KeyboardInterrupt"
            except:
                result.addError(self, self.__exc_info())
                return

            ok = False
            try:
                testMethod()
                ok = True
            except self.failureException:
                result.addFailure(self, self.__exc_info())
            except KeyboardInterrupt:
                print "KeyboardInterrupt"
            except:
                result.addError(self, self.__exc_info())

        finally:
            try:
                self.tearDown()
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self.__exc_info())
                ok = False
            if ok: result.addSuccess(self)
            result.stopTest(self)
