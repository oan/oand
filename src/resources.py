#!/usr/bin/env python
'''


Problem: On one node, be able to reach all files on all nodes.

directory
    Is the full path excluding filename. /movies/comedy/

name
    Is the name of a file. Folders don't have any name

path
    Is directory + name. /movies/comedy/aliens.avi


'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

class ResourceRoot:
    resources = None

    def __init__(self):
        self.resources = {}
        self.resources['/'] = Folder('/')

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
            self.resources[path] = Folder(path)
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

class Resource():
    directory = None
    name = None
    content = None

    def is_folder(self):
        return isinstance(self, Folder)

    def is_file(self):
        return isinstance(self, File)

    @property
    def path(self):
        return self.directory + self.name

class Folder(Resource):
    def __init__(self, path):
        path = path.rstrip('/')
        parts = path.rpartition('/')
        self.directory = parts[0] + parts[1]
        self.name = parts[2] + '/'

        self.content = []

    def add(self, content):
        self.content.append(content)

class File(Resource):
    def __init__(self, path):
        parts = path.rpartition('/')
        self.directory = parts[0] + parts[1]
        self.name = parts[2]

        self.content = 'This is the contents of the file.'

