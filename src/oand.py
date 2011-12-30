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
from oan import node_manager, meta_manager, data_manager, set_managers
from oan_daemon_base import OANDaemonBase
from oan_node_manager import OANNodeManager
from oan_meta_manager import OANMetaManager
from oan_data_manager import OANDataManager
from oan_config import OANConfig
from oan_loop import OANLoop, OANTimer

#from oan_network_node import OANNetworkNode
#from oan_server import OANServer

class OANApplication():
    config = None
    loop = None

    def __init__(self, config):
        self.config = config
        self._start_logger()

    def run(self):
        logging.info("Starting Open Archive Network (oand) for " +
                     self.config.node_name)

        set_managers(
            "None", #OANDataManager("../var/data.dat"),
            "None", #OANMetaManager(),
            OANNodeManager()
        )

        self._setup_node_manager()
        self._start_loop()
        self._connect_to_oan()

        logging.info("Stopping Open Archive Network (oand)")

    # is it possible to catch the SIG when killing a deamon and call this function.
    def stop(self):
        self._stop_loop()

    def _setup_node_manager(self):
        '''
        Prepare nodemanager to connect to OAN network.

        '''

        my_node = node_manager().create_node(
            self.config.node_uuid,
            self.config.node_domain_name,
            self.config.node_port,
            self.config.blocked
        )

        node_manager().set_my_node(my_node)
        node_manager().remove_dead_nodes()

    def _connect_to_oan(self):
        if (self.config.bff_domain_name and self.config.bff_port):
            node_manager().connect_to_oan(self.config.bff_domain_name, int(self.config.bff_port))
            logging.info("Add bff %s:%s" % (self.config.bff_domain_name, self.config.bff_port) )

    def _start_loop(self):
        self.loop = OANLoop()
        self.loop.add_timer(OANTimer(20, self.run_every_minute))   #60
        self.loop.add_timer(OANTimer(10, self.run_every_day)) #60 * 60 * 24
        self.loop.on_shutdown += [node_manager().shutdown]
        self.loop.start()

    def _stop_loop(self):
        self.loop.stop()
        self.loop.join()
        self.loop = None

    def run_every_minute(self):
        #print "run_every_minute"
        node_manager().send_heartbeat()

    def run_every_day(self):
        #print "run_every_day"
        node_manager().send_node_sync()
        node_manager().remove_dead_nodes()

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
