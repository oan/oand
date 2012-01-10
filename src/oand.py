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

import logging
import logging.handlers
from optparse import OptionParser, make_option, IndentedHelpFormatter

import oan
import uuid

from oan import loop, database, dispatcher, node_manager, meta_manager, data_manager, set_managers
from oan_daemon_base import OANDaemonBase
from oan_node_manager import OANNodeManager
from oan_meta_manager import OANMetaManager
from oan_data_manager import OANDataManager
from oan_config import OANConfig
from oan_loop import OANLoop, OANTimer
from oan_message import OANMessageDispatcher, OANMessagePing, OANMessageStoreNodes, OANMessageLoadNodes
from oan_database import OANDatabase

class OANApplication():
    config = None
    timer_every_minute = None
    timer_every_day = None
    timer_connect = None

    def __init__(self, config):
        self.config = config
        self._start_logger()

    def run(self):
        logging.info("Starting Open Archive Network (oand) for " +
                     self.config.node_name)

        set_managers(
            OANLoop(),
            OANDatabase(self.config),
            OANMessageDispatcher(self.config),
            "None", #OANDataManager("../var/data.dat"),
            "None", #OANMetaManager(),
            OANNodeManager(self.config)
        )

        database().start()
        self._setup_node_manager()
        self._setup_timers()
        self._start_loop()
        self._start_dispatcher()

        if not node_manager().get_my_node().blocked:
            loop().listen(node_manager().get_my_node())

        # wait for all thread to complete.

    # is it possible to catch the SIG when killing a deamon and call this function.
    def stop(self):
        logging.info("Stopping Open Archive Network (oand)")

        self._stop_loop()
        self._stop_dispatcher()
        database().shutdown()
        node_manager().dump()

    def _setup_timers(self):
        self.timer_every_minute = OANTimer(5, self.run_every_minute)
        self.timer_every_day = OANTimer(20, self.run_every_day)
        self.timer_connect = OANTimer(5, self._connect_to_oan)

    def _setup_node_manager(self):
        '''
        Prepare nodemanager to connect to OAN network.

        '''

        node_manager().load()
        node_manager().remove_dead_nodes()

    # maybe choose from nodelist if bff fails. just use bff if nodes list is empty.
    # our test network just know bff so if 2 fails from start there will be 2 seperate networks, for now wait for bff
    # TODO: increase sleep time after every failed.
    def _connect_to_oan(self):
        if (self.config.bff_domain_name and self.config.bff_port):

            server = loop()._server
            host, port = self.config.bff_domain_name, int(self.config.bff_port)
            print "Try connecting to bff %s:%s" % (host, port)
            #logging.info("Add bff %s:%s" % (host, port) )

            connected = False
            for bridges in server.bridges.values():
                if bridges.node.host == host and bridges.node.port == port:
                    connected = True
                    loop().remove_timer(self.timer_connect)
                    print "Connected to bff %s:%s" % (host, port)

            if not connected:
                loop().connect_to_oan(host, port)

    def _start_loop(self):
        loop().add_timer(self.timer_every_minute)
        loop().add_timer(self.timer_every_day)
        loop().add_timer(self.timer_connect)
        loop().on_shutdown += [node_manager().shutdown]
        loop().start()

    def _stop_loop(self):
        loop().stop()
        loop().join()

    def _start_dispatcher(self):
        dispatcher().start()

    def _stop_dispatcher(self):
        dispatcher().stop()
        dispatcher().join()

    def run_every_minute(self):
        #print "run_every_minute"
        node_manager().send_heartbeat()
        node_manager().dump()

    def run_every_day(self):
        #print "run_every_day"
        node_manager().send_node_sync()
        node_manager().remove_dead_nodes()

        dispatcher().process(OANMessageStoreNodes.create())

        node_manager().send(uuid.UUID('00000000-0000-dead-0000-000000000000'),
                                        OANMessagePing.create( "my test ping", 2))
                                           # send ping back and forward (2)

    def _start_logger(self,):
        my_logger = logging.getLogger()
        log_level = logging.DEBUG

        my_logger.setLevel(log_level)

        # create console handler and set level to debug
        ch1 = logging.handlers.SysLogHandler()
        ch1.setLevel(log_level)
        ch2 = logging.handlers.RotatingFileHandler(
            self.config.log_file, maxBytes=2000000, backupCount=100)
        ch2.setLevel(log_level)

        # create formatter
        formatter = logging.Formatter(
            '%(asctime)s - oand (%(process)d) - %(message)s')

        # add formatter to ch
        ch1.setFormatter(formatter)
        ch2.setFormatter(formatter)

        # add ch to logger
        my_logger.handlers = []
        my_logger.addHandler(ch1)
        my_logger.addHandler(ch2)

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

class OANApplicationStarter():
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
            formatter = IndentedHelpFormatter(max_help_position=40, width=80)
        )

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
                dest="config", default = oan.ETC_DIR + "oand.cfg",
                help="The name of the config file."),

            make_option(
                "--pid-file", metavar="FILE",
                help="The pid-file path."),

            make_option(
                "--log-file", metavar="FILE",
                help="The log-file path.")
        ]


    def _handle_positional_argument(self, options, argument):
        '''
        Handle the positional arguments from the commandline.

        '''
        config = OANConfig()
        config.set_from_file(options.config)
        config.set_from_cmd_line(options)
        config.print_options()

        if argument == 'start':
            OANDaemon(config).start()
        elif argument == 'stop':
            OANDaemon(config).stop()
        elif argument == 'restart':
            OANDaemon(config).restart()
        elif argument == 'native':
            OANApplication(config).run()
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
native           Start oand server as a reqular application."""

if __name__ == "__main__":
    OANApplicationStarter()
