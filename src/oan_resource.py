#!/usr/bin/env python
'''


Problem: On one node, be able to reach all files on all nodes.

directory
    Is the full path excluding filename. /movies/comedy/

name
    Is the name of a file or folder.

path
    Is directory + name. /movies/comedy/aliens.avi


'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import uuid

from oan_heartbeat import OANHeartBeat

class OANResourceRoot:
    resources = None

    def __init__(self):
        self.resources = {}
        self.resources['/'] = OANFolder('/')

    def _mkdir(self, directory, name):
        '''
        Create directory if not already existing.

        directory
            The folder that name should be added on. Ends with slash
            ex. /movies/comedy/

        name
            The name of the folder that should be created. Ends with slash.
            ex: romantic/

        '''
        path = directory + name
        if (not self.exist(path)):
            self.resources[path] = OANFolder(path)
            if (directory):
                self.get(directory).add(name)

        return self.get(path)

    def _mkdirs(self, path):
        parent = self.get('/')
        for part in path.strip('/').split('/'):
            parent = self._mkdir(parent.path, part + '/')

        return parent

    def set(self, resource):
        if (resource.is_folder()):
            self._mkdirs(resource.path)

        if (resource.is_file()):
            parent = self._mkdirs(resource.directory)
            parent.add(resource.name)
            self.resources[resource.path] = resource

    def exist(self, path):
        if path in self.resources:
            return True
        else:
            return False

    def get(self, path):
        return self.resources[path]

    def get_known_parent(self, path):
        '''
        Get the first known/existing parent from path.

        If path is /music/metal/danzig/ the function will check if metal exists
        and then music and the root, until finding an existing resource.

        '''
        parent_path = path.rpartition('/')[0] + "/"

        if self.exist(parent_path):
            return self.get(parent_path)
        else:
            return self.get_known_parent(parent_path.rstrip("/"))

class OANResource():
    _uuid = None
    directory = None
    name = None
    content = None
    heartbeat = None
    node_uuids = []

    def __init__(self):
        self.heartbeat = OANHeartBeat()

    def is_folder(self):
        return isinstance(self, OANFolder)

    def is_file(self):
        return isinstance(self, OANFile)

    @property
    def uuid(self):
        if not self._uuid:
            self._uuid = uuid.uuid5(
                uuid.NAMESPACE_URL, self.directory + '/' + self.name
            )
        return self._uuid

    @property
    def path(self):
        return self.directory + self.name

    @property
    def type(self):
        return self.__class__.__name__

    @classmethod
    def create_from_dict(cls, args):
        return cls (
            args['uuid'],
            args['name'],
            args['domain_name'],
            args['port'],
            args['last_heartbeat']
        )

    def get_dict(self):
        param = {}
        param['uuid'] = str(self.uuid)
        param['type'] = self.type
        param['directory'] = self.directory
        param['name'] = self.name
        param['content'] = self.content
        return param

class OANFolder(OANResource):
    def __init__(self, path):
        OANResource.__init__(self)
        path = path.rstrip('/')
        parts = path.rpartition('/')
        self.directory = parts[0] + parts[1]
        self.name = parts[2] + '/'

        self.content = []

    def add(self, content):
        self.content.append(content)

class OANFile(OANResource):
    def __init__(self, path):
        OANResource.__init__(self)
        parts = path.rpartition('/')
        self.directory = parts[0] + parts[1]
        self.name = parts[2]

        self.content = 'This is the contents of the file.'
