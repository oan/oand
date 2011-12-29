#!/usr/bin/env python
'''
Start one or more deamons on localhost to represent a OAN-network.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from time import sleep

from oand import OANDaemon
from oan_config import OANConfig

configs = {}

def start_test_network():
    global configs
    _create_config(10)

    for config in configs.itervalues():
        print "Start node [%s][%s] on port %s." % (config.node_name, config.node_uuid, config.node_port)
        OANDaemon(config).start()

def stop_test_network():
    global configs

    for config in configs.itervalues():
        print "Stop node [%s][%s] on port %s." % (config.node_name, config.node_uuid, config.node_port)
        OANDaemon(config).stop()

def _create_config(num_of_nodes):
    global configs

    for x in xrange(num_of_nodes):
        if x == 0:
            configs[x] = OANConfig(
                "xx:hh:1%s" % x,
                "server-" + str(x),
                "localhost",
                str(4000 + x)
            )
        else:
            configs[x] = OANConfig(
                "xx:hh:1%s" % x,
                "server-" + str(x),
                "localhost",
                str(4000 + x),
                "server-" + str(x-1),
                "localhost",
                str(4000 + x - 1)
            )

        configs[x].pid_file = "/tmp/oand-test-%d.pid" % x
        configs[x].log_file = "/tmp/oand-test-network.log"
