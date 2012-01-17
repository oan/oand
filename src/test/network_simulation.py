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

from oan.application import OANDaemon
from oan.config import OANConfig

configs = {}

def start_test_network():
    global configs
    _create_open_config(8)
    _create_blocked_config(2)

    for config in configs.itervalues():
        if config.blocked:
            print "Start node [%s][%s] blocked." % (config.node_name, config.node_uuid)
        else:
            print "Start node [%s][%s] on port %s." % (config.node_name, config.node_uuid, config.node_port)

        OANDaemon(config).start()

def stop_test_network():
    global configs

    for config in configs.itervalues():
        if config.blocked:
            print "Stop node [%s][%s] blocked." % (config.node_name, config.node_uuid)
        else:
            print "Stop node [%s][%s] on port %s." % (config.node_name, config.node_uuid, config.node_port)

        OANDaemon(config).stop()

def _create_open_config(num_of_nodes):
    global configs

    size = len(configs)
    for x in xrange(size, size+num_of_nodes):
        if x == 0:
            configs[x] = OANConfig(
                "00000000-0000-0000-%s-000000000000" % (4000 + x),
                "server-" + str(x),
                "localhost",
                str(4000 + x)
            )
        else:
            configs[x] = OANConfig(
                "00000000-0000-0000-%s-000000000000" % (4000 + x),
                "server-" + str(x),
                "localhost",
                str(4000 + x),
                "server-" + str(x-1),
                "localhost",
                str(4000 + x - 1)
            )

        configs[x].pid_file = "/tmp/oand-test-%d.pid" % x
        configs[x].log_file = "/tmp/oand-test-network.log"


def _create_blocked_config(num_of_nodes):
    global configs

    size = len(configs)
    for x in xrange(size, size+num_of_nodes):
        configs[x] = OANConfig(
            "00000000-0000-bbbb-%s-000000000000" % (4000 + x),
            "server-" + str(x),
            "localhost",
            str(4000 + x),
            "server-0",
            "localhost",
            str(4000),
            True
        )

        configs[x].pid_file = "/tmp/oand-test-%d.pid" % x
        configs[x].log_file = "/tmp/oand-test-network.log"





