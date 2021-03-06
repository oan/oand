#!/usr/bin/env python
'''
Proof of concept of distributed nosql RESTful database/filesystem.

# READ MORE
# http://twistedmatrix.com/documents/current/web/


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

import logging
import sys
import logging.handlers
import pickle
import os
import sys
import time

from optparse import OptionParser, make_option, IndentedHelpFormatter

from daemon import Daemon
from config import Config
from datastoremanager import SimpleDataStoreManager
from twistedserver import TwistedServer
from jsonclient import JsonClient
from networknodemanager import CircularNetworkNodeManager, NetworkNode
from objectclientserver import ObjectClient, ObjectServer
from apscheduler.scheduler import Scheduler

class OANApplication():
    _data_store_manager_class = None
    _network_node_manager_class = None
    _server_class = None
    _client_class = None

    _config = None
    _data_store_manager = None
    _network_node_manager = None
    _server = None

    _sched = Scheduler()

    def __init__(self, config, data_store_manager_class,
                 network_node_manager_class, server_class, client_class):
        self._config = config
        self._data_store_manager_class = data_store_manager_class
        self._network_node_manager_class = network_node_manager_class
        self._server_class = server_class
        self._client_class = client_class

        self._start_logger("apscheduler.scheduler", logging.WARNING)
        self._start_logger("oand", logging.DEBUG)

    @classmethod
    def create_localnetwork_circular_node(cls, config):
        return cls(config, SimpleDataStoreManager, CircularNetworkNodeManager,
                   ObjectServer, ObjectClient)

    @classmethod
    def create_twisted_circular_node(cls, config):
        return cls(config, SimpleDataStoreManager, CircularNetworkNodeManager,
                   TwistedServer, JsonClient)

    def run_every_minute(self):
        self._network_node_manager.check_heartbeat()

    def run_every_day(self):
        self._network_node_manager.remove_expired_nodes()

    def _start_scheduler(self):
        self._logger.debug("Starting scheduler")
        self._sched.add_interval_job(self.run_every_minute, minutes = 1)
        self._sched.add_interval_job(self.run_every_day, days = 1)
        self._sched.start()

    def run_server(self):
        self._logger.info("Starting Open Archive Network (oand) for " +
                          self._config.server_name)

        self._logger.debug("data_store_manager " +
                           str(self._data_store_manager_class))
        self._logger.debug("network_node_manager_class " +
                           str(self._network_node_manager_class))
        self._logger.debug("server_class " + str(self._server_class))
        self._logger.debug("client_class " + str(self._client_class))

        self._data_store_manager = self._data_store_manager_class("data.dat")

        self._network_node_manager = self._network_node_manager_class(
            self._client_class,
            self._logger)
        self._network_node_manager.remove_expired_nodes()

        self._network_node_manager.set_my_node(NetworkNode(
            self._config.server_name,
            self._config.server_domain_name,
            self._config.server_port))

        if (self._config.bff_name):
            self._network_node_manager.add_node(NetworkNode(
                self._config.bff_name,
                self._config.bff_domain_name,
                self._config.bff_port))

            self._network_node_manager.connect_to_oan()

        self._start_scheduler()
        self._network_node_manager.check_heartbeat()
        self.dbg_print_network()
        self._server = self._server_class(self._config,
                                          self._network_node_manager,
                                          self._data_store_manager)
        self._logger.info("Stopping Open Archive Network (oand)")

    def get_config(self):
        return self._config

    def get_network_node_manager(self):
        return self._network_node_manager

    def dbg_print_network(self):
        self._logger.debug("Nodes in network on " +
                           self._network_node_manager.get_my_node().get_name())
        self._logger.debug("    " + self._network_node_manager.get_dbg_nodes())

    def _start_logger(self, logger_name, log_level):
        # create logger
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(log_level)

        # create console handler and set level to debug
        ch1 = logging.handlers.SysLogHandler()
        ch1.setLevel(log_level)
        ch2 = logging.handlers.RotatingFileHandler(
            self._config.log_file, maxBytes=2000000, backupCount=100)
        ch2.setLevel(log_level)

        # create formatter
        server_name = self._config.server_name
        formatter = logging.Formatter(
            '%(asctime)s - oand (' + server_name + ') - %(message)s')

        # add formatter to ch
        ch1.setFormatter(formatter)
        ch2.setFormatter(formatter)

        # add ch to logger
        self._logger.handlers = []
        self._logger.addHandler(ch1)
        self._logger.addHandler(ch2)

class OANDaemon(Daemon):
    def __init__(self, app):
        self._app = app
        Daemon.__init__(self, app.get_config().pid_file)

    def run(self):
        self._app.run_server()

class ApplicationStarter():
    '''
    Handles all command line options/arguments and start the oand server.

    '''
    parser = None

    def __init__(self):
        '''
        Used to control the command line options, and the execution of the script.

        First function called when using the script.

        '''
        self._parser = OptionParser(
            usage = self._get_usage(),
            version = "oand " + __version__,
            add_help_option = True,
            option_list = self.get_options(),
            formatter = IndentedHelpFormatter(max_help_position=40, width=80))

        (options, args) = self._parser.parse_args()

        print self._parser.get_version()

        if len(args) != 1:
            self._parser.print_help()
        else:
            self._handle_positional_argument(options, args[0])

    def get_options(self):
        return [
            make_option(
                "-v", "--verbose", action="store_const", const=2, dest="verbose",
                help="Show more output."),

            make_option(
                "-q", "--quiet", action="store_const", const=0, dest="verbose",
                help="Show no output."),

            make_option(
                "-a", "--server-name", metavar="NAME",
                help="The server name."),

            make_option(
                "-s", "--server-domain-name", metavar="NAME",
                help="The server domain name or ip."),

            make_option(
                "-d", "--server-port", metavar="PORT", type="int",
                help="The server port number."),

            make_option(
                "-z", "--bff-name", metavar="NAME",
                help="The bff server name."),

            make_option(
                "-x", "--bff-domain-name", metavar="NAME",
                help="The bff server domain name or ip."),

            make_option(
                "-c", "--bff-port", metavar="PORT", type="int",
                help="The bff server port number."),

            make_option(
                "--defaults-extra-file", metavar="FILE",
                dest="config", default="oand.cfg",
                help="The name of the config file."),

            make_option(
                "--pid-file", metavar="FILE",
                help="The pid-file path."),

            make_option(
                "--log-file", metavar="FILE",
                help="The log-file path.")
        ]

    def handle_network(self, action):
        config = {}
        app = {}
        daemon = {}

        for x in range(10):
            x = int(x)
            print "%s daemon %d" % (action, x)
            if x == 0:
                config[x] = Config(
                  "server-" + str(x),
                  "localhost",
                  str(4000 + x)
                )
            else:
                config[x] = Config(
                  "server-" + str(x),
                  "localhost",
                  str(4000 + x),
                  "server-" + str(x-1),
                  "localhost",
                  str(4000 + x - 1)
                )

            config[x].pid_file = "/tmp/oand-%d.pid" % x
            config[x].log_file = "../log/oand-network.log"

            app[x] = OANApplication.create_twisted_circular_node(config[x])
            daemon[x] = OANDaemon(app[x])
            if (action == "start"):
                daemon[x].start()
                time.sleep(1)
            elif (action == "stop"):
                daemon[x].stop()

    def _handle_positional_argument(self, options, argument):
        '''
        Handle the positional arguments from the commandline.

        '''
        if argument == 'start-network':
            self.handle_network("start")
            return
        elif argument == 'stop-network':
            self.handle_network("stop")
            return
        elif argument == 'restart-network':
            self.handle_network("stop")
            self.handle_network("start")
            return

        config = Config()
        config.set_from_file(options.config)
        config.set_from_cmd_line(options)
        config.print_options()

        app = OANApplication.create_twisted_circular_node(config)
        daemon = OANDaemon(app)
        if argument == 'start':
            daemon.start()
        elif argument == 'stop':
            daemon.stop()
        elif argument == 'restart':
            daemon.restart()
        elif argument == 'native':
            app.run_server()
        else:
            self._parser.print_help()

    def _get_usage(self):
        '''
        Display information about how to start the daemon-server.

        '''
        return """usage: %prog [-vqf] {start|stop|restart|native|status}

Positional arguments:
start            Start oand server as a daemon.
stop             Stop oand server daemon.
restart          Retart oand server daemon.
native           Start oand server as a reqular application.

start-network    Start a network of oand daemons.
stop-network     Stop a network of oand daemons.
restart-network  Retart a network of oand daemons."""

if __name__ == "__main__":
    ApplicationStarter()
