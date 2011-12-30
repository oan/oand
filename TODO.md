HIGH-LEVEL TODO
===============
* Node-awareness
* File-awareness
* File transfer
* Optimize speed/amount-of-data
* Client
* Encryption
* VERSION 0.1

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

TODO
====

* Create UML
  http://yuml.me/1555afce

  # Help

  http://yuml.me/diagram/scruffy/class/samples

  # Code

  [note: You can stick notes on diagrams too!{bg:cornsilk}]
  [OAN]++-1>[OANDataManager]
  [OAN]++-1>[OANMetaManager]
  [OAN]++-1>[OANNodeManager]
  [OANNodeManager]++-0..*>[OANNode]
  [OANNode]++-1>[OANHeartBeat]
  [OANApp]++-1>[OANConfig]
  [OANApp]++-1>[OANServer]
  [OANApp]++-1>[OANLoop]

  # Generate new diagram

  http://yuml.me/diagram/scruffy/class/draw2



* Write test_resources and resourcemanager.

* Enable tls/ssl
  http://stackoverflow.com/questions/1085050/how-do-i-use-tls-with-asyncore

* Prefix all our classes with OAN.

* Rename server-* to node-* in oand.cfg

* Use twisted json-rpc??
  http://stackoverflow.com/questions/4738209/python-twisted-json-rpc

* Have a look att github ruby comment thing.

* Add unit test, testing many thousand nodes.

* Look more at this, giving any ideas?
  http://developer.github.com/v3/gists/

* Save all known nodes to file/db.
  Use the oan db class.

* Add oan-db-backend class system, with possiblity to store all data in sqllite,
  filesystem or other.

* HtmlValueHandler should see the difference between folder and file.

* ValueHandler (json) should see the difference between folder and file.

* Add version to http://localhost:1337/nodes and check if version is the same
  between nodes.

* Use this for all getter/setters
  http://docs.python.org/library/functions.html#property

* Lots of error checking, code comments etc.

* Have another look at
  http://entangled.svn.sourceforge.net/viewvc/entangled/

* Test this Fuse-python
  http://websaucesoftware.com/programming/python/installing-fuse-python-on-os-x-105

* Have a look at different DHT algorithms Chord, Kademlia, Pastry, OceanStore
  and Coral.

* Features we should support.
  anonymity, Byzantine fault-tolerant lookups, geographic routing and the
  efficient broadcasting of messages to enter the network.

* Try this daemon? http://pypi.python.org/pypi/python-daemon/

* Add something like this? easy_install?
  http://entangled.svn.sourceforge.net/viewvc/entangled/entangled/setup.py?revision=157&view=markup

* Add config page, looking like this
  http://www.facebook.com/editprofile.php?sk=basic
  http://www.youtube.com/account_profile

* Add security, like checking all arguments for XXS. Check owasp.

* One way to store key/value
  http://highscalability.com/blog/2011/1/10/riaks-bitcask-a-log-structured-hash-table-for-fast-keyvalue.html

Things to read
==============

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
