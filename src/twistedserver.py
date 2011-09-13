#!/usr/bin/env python
'''
Testing twisted and RESTfulnes.

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

import pickle, os, sys, time
import logging
import logging.handlers
from optparse import OptionParser

from twisted.web import server, resource, http
from twisted.internet import reactor
from twisted.web.static import File

import json

from daemon import Daemon

from SimpleDataStoreManager import SimpleSimpleDataStoreManager

class RootResource(resource.Resource):
    def __init__(self, data_store_manager):
        self._data_store_manager = data_store_manager
        resource.Resource.__init__(self)
        self.putChild('value', MessageHandler(self._data_store_manager))
        self.putChild('', File("html/index.html"))

    def getChild(self, path, request):
        logging.getLogger('oandtwisted').debug("root: " + path)
        return File("html/404.html")

class MessageHandler(resource.Resource):
    def __init__(self, data_store_manager):
        self._data_store_manager = data_store_manager
        self.isLeaf=True
        resource.Resource.__init__(self)

    def _get_filename(self, request):
        return "/".join(request.postpath)

    def render_GET(self, request):
        request.setHeader("Server", "OAND")
        filename = self._get_filename(request)
        logging.getLogger('oandtwisted').debug("value: " + filename)

        if (self._data_store_manager.hasMessage(filename)):
            request.setHeader("Content-Type", "application/json")
            request.setResponseCode(http.FOUND)
            obj = {}
            obj["filename"] = filename
            obj["data"] = self._data_store_manager.get(filename)
            return json.dumps(obj)
        else:
            request.setHeader("Content-Type", "text/html")
            request.setResponseCode(http.NOT_FOUND)
            return """
            <html><body>use post method for direct insertion or form below<br>
            <form action='/value/%s' method=POST>
            <textarea name=body>Body</textarea><br>
            <input type=submit>
            </body></html>
            """ % filename

    def render_POST(self, request):
        filename = self._get_filename(request)
        body=request.args['body'][0]
        self._data_store_manager.set(filename, body)
        return "Posted"

    def render_DELETE(self, request):
        if self._data_store_manager.exist(self.path):
            self._data_store_manager.delete(self.path)
            return """ msg %s deleted	""" % (self.path)
        else:
            return """ msg not found for hashKey: %s""" % self.path

class Child404(resource.Resource):
    isLeaf=True
    def __init__(self):
        resource.Resource.__init__(self)

    def render_GET(self, request):
        request.setHeader("Content-Type", "text/html")
        request.setResponseCode(http.NOT_FOUND)
        input_file = codecs.open("html/404.html", mode="r", encoding="utf8")
        text = input_file.read()
        html = markdown.markdown(text)

        return str(html)

    def render_POST(self, request):
        return render_GET(request)

    def render_PUT(self, request):
        return render_GET(request)

    def render_DELETE(self, request):
        return render_GET(request)

class OANApplication():
    def _start_logger(self, server_name):
        # create logger
        self._logger = logging.getLogger('oand' + server_name)
        self._logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch1 = logging.handlers.SysLogHandler()
        ch1.setLevel(logging.DEBUG)
        #ch2 = logging.handlers.RotatingFileHandler("../log/oand.log", maxBytes=2000000, backupCount=100)
        #ch2.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter(
            '%(asctime)s - oand (' + server_name + ') - %(message)s')

        # add formatter to ch
        ch1.setFormatter(formatter)
        #ch2.setFormatter(formatter)

        # add ch to logger
        self._logger.addHandler(ch1)
        #self._logger.addHandler(ch2)

    def start_server(self):
        '''
        Start the OAN server.
        '''
        self._start_logger("twisted")
        self._logger.debug("Start twisted server")
        data_store_manager = SimpleDataStoreManager("data.dat")
        reactor.listenTCP(8082, server.Site(RootResource(data_store_manager)))
        reactor.run()

class OANDaemon(Daemon):
    def __init__(self, app):
        Daemon.__init__(self, '/tmp/oand.pid', '/tmp/stdin', '/tmp/stdout','/tmp/stderr')
        self._app = app

    def run(self):
        self._app.start_server()

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
                                    usage=self._get_usage(),
                                    version="oand " + __version__,
                                    add_help_option=True)

        self._parser.add_option(
            "-v", "--verbose", action="store_const", const=2, dest="verbose",
            default=1, help="Show more output.")

        self._parser.add_option(
            "-q", "--quiet", action="store_const", const=0, dest="verbose",
            help="Show no output.")

        (options, args) = self._parser.parse_args()

        print self._parser.get_version()

        if len(args) != 1:
            self._parser.print_help()
        else:
            self._handle_positional_argument(args[0])

    def _handle_positional_argument(self, argument):
        '''
        Handle the positional arguments from the commandline.

        '''
        app = OANApplication()
        daemon = OANDaemon(app)
        if argument == 'start':
            daemon.start()
        elif argument == 'stop':
            daemon.stop()
        elif argument == 'restart':
            daemon.restart()
        elif argument == 'native':
            app.start_server()
        else:
            self._parser.print_help()

    def _get_usage(self):
        '''
        Display information about how to start the daemon-server.

        '''
        return """usage: %prog [-vqf] {start|stop|restart|native|status}

start - Start oand server as a deamon.
stop - Stop oand server deamon.
restart - Retart oand server deamon.
native - Start oand server as a reqular application."""

if __name__ == "__main__":
    ApplicationStarter()