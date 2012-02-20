#!/usr/bin/env python
'''
Proof of concept of distributed nosql RESTful database/filesystem.

# Test with
# curl -d "hashKey=key1;body=fulltextbodynoencoding" http://localhost:8082/train
# Content-Type: application/json
# json.dumps(args)

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import time
from oan.util import log
from oan import manager
from oan.manager import network, database, dispatcher, node_manager, meta_manager, data_manager
from oan.util.daemon_base import OANDaemonBase
from oan.util.signal_handler import OANTerminateInterrupt, OANStatusInterrupt
from oan.node_manager.node_manager import OANNodeManager
from oan.meta_manager import OANMetaManager
from oan.data_manager import OANDataManager
from oan.config import OANConfig
from oan.database.database import OANDatabase

from oan.node_manager.command import (OANCommandStaticHeartbeat,
    OANCommandStaticLoadNodes, OANCommandStaticStoreNodes,
    OANCommandStaticSyncNodes)

from oan.dispatcher.dispatcher import OANDispatcher
from oan.network.network import OANNetwork, OANNetworkTimer
from oan.network.command import (OANNetworkCommandListen,
    OANNetworkCommandConnectOan)


class OANApplication():
    config = None
    _is_terminating = False

    def __init__(self, config):
        self._is_terminating = False
        self.config = config

    def start(self):
        log.info("Starting Open Archive Network for " + self.config.node_name)

        manager.setup(
            "None", #OANDataManager("../var/data.dat"),
            "None", #OANMetaManager(),
            OANNodeManager(self.config),
            OANDatabase(self.config),
            OANDispatcher(),
            OANNetwork()
        )

        self._setup_timers()

        dispatcher().execute(OANCommandStaticLoadNodes)
        network().execute(OANNetworkCommandListen.create(self.config.node_port))

        if (self.config.bff_port and self.config.bff_domain_name):
            print "connecting to oan...."
            network().execute(OANNetworkCommandConnectOan.create(
                self.config.bff_domain_name, self.config.bff_port))

    def stop(self):
        log.info("Stopping Open Archive Network")
        manager.shutdown()

    def _setup_timers(self):
        network().add_timer(OANNetworkTimer(5, self.run_every_minute))
        network().add_timer(OANNetworkTimer(20, self.run_every_day))

    def run_every_minute(self):
        log.debug("run_every_minute")
        dispatcher().execute(OANCommandStaticHeartbeat)
        node_manager().dump()

    def run_every_day(self):
        log.debug("run_every_day")
        dispatcher().execute(OANCommandStaticStoreNodes)
        dispatcher().execute(OANCommandStaticSyncNodes)

    def get_node_info(self):
        return node_manager.get_my_node().get()


    # # maybe choose from nodelist if bff fails. just use bff if nodes list is empty.
    # # our test network just know bff so if 2 fails from start there will be 2 seperate networks, for now wait for bff
    # # TODO: increase sleep time after every failed.
    # def _connect_to_oan(self):
    #     if (self.config.bff_domain_name and self.config.bff_port):

    #         server = loop()._server
    #         host, port = self.config.bff_domain_name, int(self.config.bff_port)
    #         log.info("Try connecting to bff %s:%s" % (host, port))
    #         #log.info("Add bff %s:%s" % (host, port) )

    #         connected = False
    #         for bridges in server.bridges.values():
    #             if bridges.node.state == OANNetworkNodeState.CONNECTED:
    #                 connected = True
    #                 loop().remove_timer(self.timer_connect)
    #                 log.info("Connected to bff %s:%s" % (host, port))

    #         if not connected:
    #             loop().connect_to_oan(host, port)



class OANDaemon(OANDaemonBase):
    _app = None

    def __init__(self, config):
        self._app = OANApplication(config)
        OANDaemonBase.__init__(
            self,
            self._app.config.pid_file,
            '/dev/null',
            "%s.stdout" % self._app.config.log_file,
            "%s.stderr" % self._app.config.log_file
        )


    def run(self):
        # Need to start loggign again for deamon. Couldn't fork the looging
        # state from applications starter.
        log.setup(
            self._app.config.syslog_level,
            self._app.config.stderr_level,
            self._app.config.log_level, self._app.config.log_file
        )

        self._app.start()

        while True:
            try:
                self.wait()

            except OANStatusInterrupt, e:
                print e
            except OANTerminateInterrupt, e:
                break

        print "kkkkkkkkkkkkkkkkkkkkkkkkkkkk"
        self._app.stop()
