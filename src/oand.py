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
import logging.handlers
from apscheduler.scheduler import Scheduler
from optparse import OptionParser, make_option, IndentedHelpFormatter
from twisted.internet import reactor

from oan import node_manager, meta_manager, data_manager, set_managers
from oandaemonbase import OANDaemonBase
from oannodemanager import OANNodeManager
from oanmetamanager import OANMetaManager
from oandatamanager import OANDataManager
from oanconfig import OANConfig
from oannetworknode import OANNetworkNode
from oanserver import OANServer

class OANApplication():
    config = None

    _sched = Scheduler()

    def __init__(self, config):
        self.config = config

        self._start_logger(logging.getLogger("apscheduler.scheduler"), logging.WARNING)
        self._start_logger(logging.getLogger(), logging.DEBUG)

    def setup_node_manager(self):
        '''
        Prepare nodemanager to connect to OAN network.

        '''
        node_manager().remove_expired_nodes()
        node_manager().set_my_node(OANNetworkNode(
            self.config.node_uuid,
            self.config.node_name,
            self.config.node_domain_name,
            self.config.node_port
        ))

        if (self.config.bff_domain_name and self.config.bff_port):
            url = "%s:%s" % (self.config.bff_domain_name, self.config.bff_port)
            logging.info("Add bff %s" % url)
            reactor.callLater(1, node_manager().connect_to_oan, url)

    def run(self):
        logging.info("Starting Open Archive Network (oand) for " +
                     self.config.node_name)

        set_managers(
            OANDataManager("../var/data.dat"),
            OANMetaManager(),
            OANNodeManager()
        )
        self.setup_node_manager()

        self._start_scheduler()

        OANServer(self.config)
        reactor.run()

        logging.info("Stopping Open Archive Network (oand)")

    def _start_scheduler(self):
        logging.debug("Starting scheduler")
        self._sched.add_interval_job(self.run_every_minute, minutes = 1)
        self._sched.add_interval_job(self.run_every_day, days = 1)
        self._sched.start()

    def run_every_minute(self):
        node_manager().check_heartbeat()

    def run_every_day(self):
        node_manager().remove_expired_nodes()

    def _start_logger(self, my_logger, log_level):
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
        _app = OANApplication(config)
        Daemon.__init__(self, self._app.config.pid_file)

    def run(self):
        _app.run()

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
                dest="config", default="../etc/oand.cfg",
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
