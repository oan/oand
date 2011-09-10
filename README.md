README
======
This is a small research project about a distibuted database/filesystem

Tests
-----

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

Things to test
===============

* Fuse-python
  http://websaucesoftware.com/programming/python/installing-fuse-python-on-os-x-105

DHT
---

Different DHT algorithms Chord, Kademlia, Pastry, OceanStore and Coral.

Features: anonymity, Byzantine fault-tolerant lookups, geographic routing and the efficient broadcasting of messages to enter the network.

General links to good reading
-----------------------------

* http://www.linuxjournal.com/article/6797

Not read by Daniel
------------------
* http://thalassocracy.org/achord/achord-iptps.html
* http://www.pdos.lcs.mit.edu/chord
* http://pdos.csail.mit.edu/papers/cfs:sosp01/
* http://blanu.net/curious_yellow.html
* http://en.wikipedia.org/wiki/Kademlia
* http://www.cs.rice.edu/Conferences/IPTPS02/
* http://wiki.vuze.com/w/Distributed_tracker