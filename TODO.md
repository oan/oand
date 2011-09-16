TODO
====

# Every node has a list with all other nodes, both online and offline.
  Attributes: node_id, ip, port, last_heartbeat

# When a connection to the OAN is done, a connection to the BFF or other known
  node are performed, and a list of all nodes are requested.

# If the last heartbeat is done 5-10 minutes ago, do a new heartbeat/ping
  to that node.

# If the last succeded heartbeat to any node is done 10 minutes ago, assume
  we are or has been an inactive node and perform a new connection.

# Offline nodes are deleted from the list when they have been inaccessiable
  for more than 365 days.

* Add something similar to this.
  http://entangled.svn.sourceforge.net/viewvc/entangled/entangled/examples/create_network.py?revision=81&view=markup

* HtmlValueHandler should see the difference between folder and file.

* ValueHandler (json) should see the difference between folder and file.

* When touch_last_heartbeat is executed by an unknown node, do a connect
  to that node and retrive a list of nodes.

* Save all known nodes to file/db.
  Use the oan db class.

* Add unit test, testing many thousand nodes.

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
