README
======
This is a small research project about a distibuted nosql database/filesystem.

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

Requirements
============

- Python 2.x or later
- ??Twisted core

Optional:
- ??Epydoc (for building API documentation)

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