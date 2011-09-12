#!/usr/bin/env python


# READ MORE
# http://twistedmatrix.com/documents/current/web/

import pickle, os, sys, time
import logging
import logging.handlers

from twisted.web import server, resource, http
from twisted.internet import reactor
from twisted.web.static import File

import markdown
import json
import codecs

from daemon import Daemon
# TODO, try this daemon??
# http://pypi.python.org/pypi/python-daemon/


class MessageStore(object):
    """class for managing messages in the form: md5hash:text"""

    messages = None
    filename = None

    def __init__(self, filename):
        self.filename = filename
        if os.path.exists(filename):
            self.messages = pickle.load(file(filename, 'r+b'))
        else:
            self.messages = {}

    def save(self):
        pickle.dump(self.messages, file(self.filename, 'w+b'))

    def hasMessage(self, hashKey):
        return self.messages.has_key(hashKey)

    def listMessageKeys(self):
        return self.messages.keys()

    def listMessages(self):
        return self.messages.items()

    def getMessage(self, hashKey):
        return self.messages[hashKey]

    def setMessage(self, hashKey, content):
        self.messages[hashKey] = content
        self.save()

    def delMessage(self, hashKey):
        del(self.messages[hashKey])

class RootResource(resource.Resource):
    def __init__(self, messageStore):
        self.messageStore = messageStore
        resource.Resource.__init__(self)
        self.putChild('value', MessageHandler(self.messageStore))
        self.putChild('', File("html/index.html"))

    def getChild(self, path, request):
        logging.getLogger('oandtwisted').debug("root: " + path)
        return Child404()

class MessageHandler(resource.Resource):
    def __init__(self, messageStore):
        self.messageStore = messageStore
        self.isLeaf=True
        resource.Resource.__init__(self)

    def _get_filename(self, request):
        return "/".join(request.postpath)

    def render_GET(self, request):
        request.setHeader("Server", "OAND")
        filename = self._get_filename(request)
        logging.getLogger('oandtwisted').debug("value: " + filename)

        if (self.messageStore.hasMessage(filename)):
            request.setHeader("Content-Type", "application/json")
            request.setResponseCode(http.FOUND)
            obj = {}
            obj["filename"] = filename
            obj["data"] = self.messageStore.getMessage(filename)
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
        self.messageStore.setMessage(filename, body)
        return "Posted"

    def render_DELETE(self, request):
        if self.messageStore.hasMessage(self.path):
            self.messageStore.delMessage(self.path)
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
        messageStore = MessageStore("data.dat")
        reactor.listenTCP(8082, server.Site(RootResource(messageStore)))
        reactor.run()

class OAND(Daemon):
    def __init__(self, app):
        Daemon.__init__(self, '/tmp/oand.pid', '/tmp/stdin', '/tmp/stdout','/tmp/stderr')
        self._app = app

    def run(self):
        self._app.start_server()

class CmdLine():
    def handle_cmd_line(self):
        '''
        Handle the commandline commands.
        start - Will create pid file and start server.
        stop - Will remove pid file and stop server.
        restart - Will run stop and start.
        '''
        if len(sys.argv) == 2:
            app = OANApplication()
            daemon = OAND(app)
            if 'start' == sys.argv[1]:
                daemon.start()
            elif 'stop' == sys.argv[1]:
                daemon.stop()
            elif 'restart' == sys.argv[1]:
                daemon.restart()
            elif 'native' == sys.argv[1]:
                app.start_server()
            else:
                print "Unknown command: %s" % sys.argv[1]
                self.print_usage()
                sys.exit(2)
            sys.exit(0)
        else:
            self.print_usage()
            sys.exit(2)

    def print_usage(self):
        '''Display information about how to start the daemon-server.'''
        print "usage: %s start|stop|restart|native" % sys.argv[0]

if __name__ == "__main__":

    cmd_line = CmdLine()
    cmd_line.handle_cmd_line()

# Test with
# curl -d "hashKey=key1;body=fulltextbodynoencoding" http://localhost:8082/train
# Content-Type: application/json
# json.dumps(args)
