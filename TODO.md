HIGH-LEVEL TODO
===============
* Node-awareness
* File-awareness
* File transfer
* Optimize speed/amount-of-data
* Client
* Encryption

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

VERSION 0.1 - NODE AWARENESS
============================

All nodes should be able to communicate, send heartbeats, sync-nodes,
store node info in datbase, can handle nodes that comes and goes. All is
well written with unit test and comments.

* Test all unit tests.

* Unittest and nicing up passthrou.

* Turn on logging for a unit test or a logfile for each unittest.

* Martin - Go through all network interfaces. Try to connect to OAN with each of them.
  The first internal ip/interface that can connect, will be used to bind the
  server. The external ip will be returned from OAN and will be used in the
  node-list.
  https://github.com/systemconsole/syco/blob/master/bin/common/net.py

* Daniel - Check doctest
  http://docs.python.org/library/doctest.html

* Daniel - Continous testing with git hooks.

* Daniel - Check buildout
  Check http://peak.telecommunity.com/DevCenter/setuptools
  Add setup.php??
  http://entangled.svn.sourceforge.net/viewvc/entangled/entangled/setup.py?revision=157&view=markup

* Daniel - Read
  http://www.ibm.com/developerworks/aix/library/au-cleancode/index.html

* Daniel - Check http://readthedocs.org/

* Daniel - Check http://pypi.python.org/pypi/virtualenv for isolated env

* Daniel - Check http://nedbatchelder.com/code/coverage/

* Martin - Collect statistics from all nodes.

* Decide which threads that are allowed to use certain managers. Or if we
  need more queues/thread-looks.

* Organize codes in more folders/packages.

* Rename src folder to lib/pkg?? What are others using?

* Test if queues are faster/better than threads locks.

* Add unit test, testing many thousand nodes.

* Add comments.

* An invalid command (send_ping) should print the help text
  (OANShell.help_send_ping) (all cmds).

* Daniel - test-all  -v -p *heartbeat* -n -t
  Only display trace output for unit test files.

VERSION 0.2
===========

* A simple http shell, where you can see status of oan.

* Write test_resources and resourcemanager.

* Enable tls/ssl
  http://stackoverflow.com/questions/1085050/how-do-i-use-tls-with-asyncore

* Prefix all our classes with OAN.

* Rename server-* to node-* in oand.cfg

* Daniel - Have a look att github ruby comment thing.

* Look more at this, giving any ideas for REST?
  http://developer.github.com/v3/gists/

* HtmlValueHandler should see the difference between folder and file.

* ValueHandler (json) should see the difference between folder and file.

* Add version to http://localhost:1337/nodes and check if version is the same
  between nodes.

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

* Rewrite deamon to work with windows.

* Test oand with windows.

* Add config page, looking like this
  http://www.facebook.com/editprofile.php?sk=basic
  http://www.youtube.com/account_profile

* Add security, like checking all arguments for XXS. Check owasp.

* One way to store key/value
  http://highscalability.com/blog/2011/1/10/riaks-bitcask-a-log-structured-hash-table-for-fast-keyvalue.html

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
