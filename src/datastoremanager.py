#!/usr/bin/env python
'''
Storing data for OAND

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from abc import ABCMeta, abstractmethod
import pickle
import os

class SimpleDataStoreManager(object):
    """
    Managing stored data in the form: path:value

    """

    _data = None
    _filename = None

    def __init__(self, filename):
        self._filename = filename
        self._load()

    def _load(self):
        if os.path.exists(self._filename):
            self._data = pickle.load(file(self._filename, 'r+b'))
        else:
            self._data = {}

    def _save(self):
        pickle.dump(self._data, file(self._filename, 'w+b'))

    def exist(self, hashKey):
        return self._data.has_key(hashKey)

    def set(self, path, data):
        self._data[path] = data
        self._save()

    def get(self, path):
        return self._data[path]

    def delete(self, path):
        if self.exist(path):
            del(self._data[path])

    def list(self, path):
        fake_list = []
        fake_list.append(path.strip("/") + "/movies/alien.avi")
        fake_list.append(path.strip("/") + "/movies/aliens.avi")
        fake_list.append(path.strip("/") + "/movies/Terminator-2.avi")
        return fake_list
