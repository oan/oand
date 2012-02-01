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

from oan.util import log
from oan.manager import network, database, dispatcher, node_manager, meta_manager, data_manager, setup
from oan.daemon_base import OANDaemonBase
from oan.node_manager import OANNodeManager
from oan.meta_manager import OANMetaManager
from oan.data_manager import OANDataManager
from oan.config import OANConfig
from oan.database import OANDatabase
from oan.dispatcher.command import (OANCommandStaticHeartbeat,
    OANCommandStaticLoadNodes, OANCommandStaticStoreNodes,
    OANCommandStaticSyncNodes, OANCommandStaticGetNodeInfo)

from oan.dispatcher.dispatcher import OANDispatcher
from oan.network.network import OANNetwork, OANTimer
from oan.network.command import OANNetworkCommandListen


class OANApplication():
    config = None

    def __init__(self, config):
        self.config = config



    def run(self):
        log.info("Starting Open Archive Network for " + self.config.node_name)

        setup(
            OANNetwork(),
            OANDatabase(self.config),
            OANDispatcher(self.config),
            "None", #OANDataManager("../var/data.dat"),
            "None", #OANMetaManager(),
            OANNodeManager(self.config)
        )

        self._setup_timers()

        dispatcher().execute(OANCommandStaticLoadNodes)
        network().execute(OANNetworkCommandListen.create(self.config.node_port))


    # TODO: is it possible to catch the SIG when killing a deamon and call this function.
    def stop(self):
        log.info("Stopping Open Archive Network")

        network().shutdown()
        dispatcher().shutdown()
        database().shutdown()



    def _setup_timers(self):
        network().add_timer(OANTimer(5, self.run_every_minute))
        network().add_timer(OANTimer(20, self.run_every_day))



    def run_every_minute(self):
        log.debug("run_every_minute")
        dispatcher().execute(OANCommandStaticHeartbeat)

        #node_manager().send_heartbeat()
        node_manager().dump()



    def run_every_day(self):
        log.debug("run_every_day")
        dispatcher().execute(OANCommandStaticStoreNodes)
        dispatcher().execute(OANCommandStaticSyncNodes)

    def get_node_info(self):
        return dispatcher().get(OANCommandStaticGetNodeInfo)



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
    #             if bridges.node.state == OANNetworkNodeState.connected:
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
            self._app.config.syslog_level, self._app.config.stderr_level,
            self._app.config.log_level, self._app.config.log_file
        )
        self._app.run()
