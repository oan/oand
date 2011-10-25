#!/usr/bin/env python
'''
Test cases for Config.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import unittest
from resources import *
from test_heartbeat import TestHeartBeat

class TestResources(TestHeartBeat):
    def setUp(self):
        self._res = ResourceRoot()
        self._res.set(Folder('/movies/'))
        self._res.set(File('/movies/aliens.avi'))
        self._res.set(Folder('/movies/comedy/'))
        self._res.set(Folder('/movies/action/'))
        self._res.set(File('/movies/drama/comedy/thriller/sci-fi/7even.avi'))

    def test_exist(self):
        self.assertEqual(self._res.exist('/'), True)
        self.assertEqual(self._res.exist('/movies/'), True)
        self.assertEqual(self._res.exist('/movies/aliens.avi'), True)
        self.assertEqual(self._res.exist('/movies/comedy/'), True)
        self.assertEqual(self._res.exist('/movies/action/'), True)

    def test_get(self):
        self.assertEqual(self._res.get('/').content, ['movies/'])
        self.assertEqual(self._res.get('/movies/').content, ['aliens.avi', 'comedy/', 'action/', 'drama/'] )
        self.assertEqual(self._res.get('/movies/aliens.avi').content, 'This is the contents of the file.')
        self.assertEqual(self._res.get('/movies/comedy/').content, [])
        self.assertEqual(self._res.get('/movies/action/').content, [])

    def test_verify_root_tree(self, path='/'):
        resource = self._res.get(path)

        if resource.is_folder():
            for content in resource.content:
                self.assertEqual(resource.is_folder(), True)
                self.test_verify_root_tree(path + content)

        if resource.is_file():
            self.assertEqual(resource.is_file(), True)
            self.assertEqual(len(resource.name) > 1, True)
            self.assertEqual(len(resource.content) > 1, True)
            self.assertEqual(resource.path, path)

    def test_heartbeat(self):
        '''
        Same tests that can be found in test_heartbeat.py
        '''
        hb = self._res.get('/').heartbeat
        TestHeartBeat.test_heartbeat(self, hb)

# class TestResourceManager(unittest.TestCase):
#     def setup(self):
#         self._res1 = ResourceRoot()
#         networkNodeManager = NetworkNodeManager()
#         self.manager = ResourceManager(self._res1, networkNodeManager)

#     def test_get(self):
#         self.manager.get('/')
#         self.manager.get('/music/')
#         self.manager.get('/music/queen.mp3')

#         self.manager.refresh()


if __name__ == '__main__':
    unittest.main()
