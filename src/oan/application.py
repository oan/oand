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
from oan import loop, database, dispatcher, node_mgr, meta_mgr, data_mgr, set_managers
from oan.daemon_base import OANDaemonBase
from oan.node_manager import OANNodeManager, OANNetworkNodeState
from oan.meta_manager import OANMetaManager
from oan.data_manager import OANDataManager
from oan.config import OANConfig
from oan.loop import OANLoop, OANTimer
from oan.message import OANMessagePing, OANMessageStoreNodes, OANMessageLoadNodes
from oan.dispatcher import OANMessageDispatcher
from oan.dispatcher.message import OANMessageStaticGetNodeInfo
from oan.database import OANDatabase

class OANApplication():
    config = None
    timer_every_minute = None
    timer_every_day = None
    timer_connect = None

    def __init__(self, config):
        self.config = config

    def run(self):
        log.info("Starting Open Archive Network (oand) for " +
                     self.config.node_name)

        set_managers(
            OANLoop(),
            OANDatabase(self.config),
            OANMessageDispatcher(self.config),
            "None", #OANDataManager("../var/data.dat"),
            "None", #OANMetaManager(),
            OANNodeManager(self.config)
        )

        #database().start()
        self._setup_node_manager()
        self._setup_timers()
        #self._start_loop()
        self._start_dispatcher()

        # if not node_mgr().get_my_node().blocked:
        #     loop().listen(node_mgr().get_my_node())

        # wait for all thread to complete.

    # is it possible to catch the SIG when killing a deamon and call this function.
    def stop(self):
        log.info("Stopping Open Archive Network (oand)")

        #self._stop_loop()
        self._stop_dispatcher()
        database().shutdown()
        node_mgr().dump()

    def _setup_timers(self):
        self.timer_every_minute = OANTimer(5, self.run_every_minute)
        self.timer_every_day = OANTimer(20, self.run_every_day)
        self.timer_connect = OANTimer(5, self._connect_to_oan)

    def _setup_node_manager(self):
        '''
        Prepare nodemanager to connect to OAN network.

        '''

        node_mgr().load()
        node_mgr().remove_dead_nodes()

    # maybe choose from nodelist if bff fails. just use bff if nodes list is empty.
    # our test network just know bff so if 2 fails from start there will be 2 seperate networks, for now wait for bff
    # TODO: increase sleep time after every failed.
    def _connect_to_oan(self):
        if (self.config.bff_domain_name and self.config.bff_port):

            server = loop()._server
            host, port = self.config.bff_domain_name, int(self.config.bff_port)
            log.info("Try connecting to bff %s:%s" % (host, port))
            #log.info("Add bff %s:%s" % (host, port) )

            connected = False
            for bridges in server.bridges.values():
                if bridges.node.state == OANNetworkNodeState.connected:
                    connected = True
                    loop().remove_timer(self.timer_connect)
                    log.info("Connected to bff %s:%s" % (host, port))

            if not connected:
                loop().connect_to_oan(host, port)

    def _start_loop(self):
        # loop().add_timer(self.timer_every_minute)
        # loop().add_timer(self.timer_every_day)
        # loop().add_timer(self.timer_connect)
        #loop().on_shutdown += [node_mgr().shutdown]
        #loop().start()
        pass

    def _stop_loop(self):
        #loop().stop()
        #loop().join()
        pass

    def _start_dispatcher(self):
        pass

    def _stop_dispatcher(self):
        dispatcher().shutdown()

    def run_every_minute(self):
        log.debug("run_every_minute")
        node_mgr().send_heartbeat()
        node_mgr().dump()

    def run_every_day(self):
        log.debug("run_every_day")
        node_mgr().send_node_sync()
        node_mgr().remove_dead_nodes()

        dispatcher().execute(OANMessageStoreNodes.create())

        node_mgr().send(uuid.UUID('00000000-0000-dead-0000-000000000000'),
                                        OANMessagePing.create( "my test ping", 2))
                                           # send ping back and forward (2)
    def get_node_info(self):
        #return OANMessageStaticGetNodeInfo.execute()
        return dispatcher().get(OANMessageStaticGetNodeInfo)

class OANDaemon(OANDaemonBase):
    _app = None

    def __init__(self, config):
        self._app = OANApplication(config)
        OANDaemonBase.__init__(
            self,
            self._app.config.pid_file,
            '/dev/null',
            "%s.stdout" % self._app.config.pid_file,
            "%s.stderr" % self._app.config.pid_file
        )

    def run(self):
        self._app.run()
