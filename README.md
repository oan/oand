README
======
This is a small research project about a distibuted nosql database/filesystem..

/etc/oand.conf
--------------
        # The OAN deamon
        [oand]
        server-name = this-is-a-server-name
        server-domain-name = www.cybercow.se
        server-port = 4000
        bff-name = LeetServer
        bff-domain-name =  oand.amivono.com
        bff-port =  1337

        # The OAN fuse client
        [oan]
        mount-point=/
        server-name = this-is-a-server-name
        server-domain-name = www.cybercow.se
        server-port = 4000

/etc/init.d/oand start
----------------------

This will start the daemon, and expose a RESTful interface on the server-domain-
name and server-port defined in the config file. You can now access the
RESTful api on the following links

        https://domain:port/value/

Will return a list will all folders and files in the root directory.

        https://domain:port/value/a-folder/a-file.txt

Will return the contents of the file "a-file.txt" that exists in "a-folder".

Network Feature List
--------------------
* Asyncront message system, no functions should stop the "main-loop".
* Auto-reconnect.
* Either client or server could be firewalled, and the other side do the connections.
  Requires TCP.
* Limit the number of open sockets. We don't like 1000 connections at the same time.
* Possible to unit test.
* Possible to execute io and cpu calls with low priority and don't hang the computer.
* REST-api
* Easy to work with.
* Stable code.
* SSL/TLS enabled

Requirements
============

- Python 2.x or later
- ??Twisted core

Optional:
- ??Epydoc (for building API documentation)

Howto Links
===========

Twisted Unit testing
http://twistedmatrix.com/documents/current/core/howto/trial.html
http://twistedmatrix.com/trac/wiki/TwistedTrial

Twisted Programming beginner to advanced
http://krondo.com/?p=1209

Twisted deffered
http://ezyang.com/twisted/defer2.html
http://twistedmatrix.com/documents/current/core/howto/deferredindepth.html


Install
=======

Ubuntu 10.10
------------

        sudo apt-get install python-setuptools
        sudo easy_install apscheduler
        mkdir /usr/local/oand
        cd /usr/local/oand
        git clone git://github.com/oan/oand.git
        cd src
        ./oand start

How to run all tests
====================

All unit tests can be found in oand/src/tests. These tests can either be
executed separately, or all at the same time.

To run all tests

    $ cd oand/src
    $ . test.env
    $ ./tools/testall.py

To execute them separatley

    $ cd oand/src
    $ . test.env
    $ ./tests/test_oand.py

License information
===================

Copyright (C) 2008-2011 Amivono AB, Sweden
See AUTHORS for all authors and contact information.

License: None at the moment ; see COPYING

Hur funkar det.
===============

* Varje node har en lista med alla andra noder, (node_id, ip, port, last_heartbeat)
  både som är online och offline.

* Offline noder plockas bort ifrån listan efter X dagar.

* Om last_heartbeat är mellan 5-10 minuter, görs ett ping request till varje node.

* Om senaste lyckade heartbeaten är gjord för längre än 10 minuter sedan,
  gör en ny connection.

* Vid en connection anropas BFF (eller annat känt ip) och efterfrågar lista
  med alla aktiva noder i nätet.


 API Documentation
 =================

 This describes the resources that make up the official OAN API v1. If you have
 any problems or requests please contact us through github https://github.com/oan.

Schema
------

All API access is over HTTPS, and accessed from the domain name and port
specified in oand.cfg. All data is sent and received as JSON

Blank fields are included as null instead of being omitted

        $ curl -i https://localhost:8082

        HTTP/1.1 200 OK
        Content-Type: application/json
        Status: 200 OK
        X-RateLimit-Limit: 5000
        X-RateLimit-Remaining: 4999
        Content-Length: 2

        {}

All timestamps are returned in ISO 8601 format:

        YYYY-MM-DDTHH:MM:SSZ

This API is based on the same RESTful standard as
[(github v3)](http://developer.github.com/v3/)

curl -X POST -d 'json={"port": "1338", "last_heartbeat": "2011-09-17T11:37:32Z", "name": "dali-book", "domain_name": "localhost"}' http://localhost:1337/heartbeat


NetworkStorageManager
---------------------

Node-1:/movie/aliens.avi
Node-2:/movie/aliens.avi
Node-2:/music/danzig.mp3
Node-3:/src/oand.py

mount.oand /mnt/oand
ls /mnt/oand
movie
music
src

ls /mnt/oand/movie
aliens.avi


NetworkStorageManager
---------------------
files = [File(), File()]

list_files(path)
get_file(path, name)
put_file(path, name, data)

get_filelist()
send_filelist()


File
---------------------
path = /movie/
name = NULL
nodes = ['node-1', 'node-2', 'node-3']
data = NULL

File
---------------------
path = /movie/
name = aliens.avi
nodes = ['node-1', 'node-2']
data = NULL





class data_store_manager
    resources = Resources()

    def exist(path):
        resources.exist(path)

    def get(path):
        resources.get(path)

class Resources:
    list{'/movies/'} = folder
    list{'/movies/aliens.avi'} = file
    list{'/movies/comedy/'} = folder
    list{'/movies/action/'} = folder('andra filmer')
    list{'/movies/action/'} = File('RAMBO.AVI')

    def exist(path):
        if path in self.list:
            return true
        else:
            return false

    get(path)
        resource = self.list['path']
        if is_instance(resource, file):
            return resource.value
        elif is_instance(resource, folder):
            return resource.list

class Folder():
    list = ['comedy/', 'action/', 'aliens.avi']

class File():
    path = '/movies/'
    name = 'aliens.avi'
    value = 'This is the contents of the file.'


class Resource
    path = '/movies/'

    resources = {'action/' = Resource('action/'), 'comedy/', Resource('comedy/')}
    files = {'aliens.avi' = File('aliens.avi')}

    def __init__(self, path, last_changed):

    def exist(path):

    def get(path):

---------
folders['/']             = Resource()
folders['/movie']        = Resource()
folders['/movie/action'] = Resource()


Resource
--------
path = '/movie/'
folder = ['/action', '/comedy'] (Resource())
file= ['aliens.avi']  (File())

File
---------------------
path = /movie/
name = aliens.avi
nodes = ['node-1', 'node-2']
data = NULL










