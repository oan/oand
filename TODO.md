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

* Unittest passthrou.
  # Test with more workers and passthru at the same time.
  * Alternative name for OANPassthru = OANMessageQueue??

* Unittest and nicing up OANNetworkNode.

* @synchronized(lock) decorator.

* Go through all unit tests.

* Organize codes in more folders/packages.

* Martin - Go through all network interfaces. Try to connect to OAN with each of them.
  The first internal ip/interface that can connect, will be used to bind the
  server. The external ip will be returned from OAN and will be used in the
  node-list.
  https://github.com/systemconsole/syco/blob/master/bin/common/net.py

* Decide which threads that are allowed to use certain managers. Or if we
  need more queues/thread-looks.

* Martin - Collect statistics from all nodes.

* An invalid command (send_ping) should print the help text
  (OANShell.help_send_ping) (all cmds).

* Add unit test, testing many thousand nodes.

* Add comments.

* Both read http://www.python.org/dev/peps/pep-0008/

* Execute and modify bin/check

* Mock
  http://www.voidspace.org.uk/python/mock/getting-started.html

VERSION 0.2
===========

* Read/learn googles python guide
  http://google-styleguide.googlecode.com/svn/trunk/pyguide.html

* Rename src folder to lib/pkg?? What are others using?

* More to read
  http://python.net/~goodger/projects/pycon/2007/idiomatic/handout.html
  http://ivory.idyll.org/articles/advanced-swc/

* Try http://pythoscope.org/tutorial

* Clean python code, gets some ideas?
  http://darcs.idyll.org/~t/projects/twill/twill/

* Run http://sourceforge.net/projects/pymetrics/ or pygenie
  on our source code.

* Use http://readthedocs.org/ and http://sphinx.pocoo.org/
  to create good looking documentation

* test-all  -v -p *heartbeat* -n -t
  Only display trace output for unit test files.

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

* Decide if we should use doctest
  http://docs.python.org/library/doctest.html

* Figure out if we can use git hooks for Continous testing. Or anyother
  populare python tool

* Daniel - Check buildout
  Check http://peak.telecommunity.com/DevCenter/setuptools
  Add setup.php??
  http://entangled.svn.sourceforge.net/viewvc/entangled/entangled/setup.py?revision=157&view=markup

* Check if http://pypi.python.org/pypi/virtualenv could be useful for us, to
  isolate the oan environment.

* Use http://nedbatchelder.com/code/coverage/ or similare to verify unit test
  coverage.
  http://darcs.idyll.org/~t/projects/figleaf/doc/
  nosetests -v --with-coverage --cover-package=highlight --with-doctest\
     --cover-erase --exe

* make number of workers dynamic start a new if all are used, it a
  worker is idle for a period of time stop the worker.

* Check code complexity
  http://sourceforge.net/projects/pymetrics/

* Run pylint on all code.
  Add to a script that can easily be executed.
  http://www.logilab.org/857

* Check for dublicate code
  http://clonedigger.sourceforge.net/

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
