#!/usr/bin/env python
"""
Network thread that handles all the network traffic

"""

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import requests
from time import sleep
from threading import Thread
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class OANHttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?")

    def do_POST(self):


        ret = dispatcher.get(message)
        node = node_manger().get_node(oanid)
        for node.out_queue:
            respones.add_message(message)





class OANHTTPServer(Thread):
    _server = None
    _running = None
    _port = None

    def __init__(self, port):
        self._running = True
        self._port = port

        Thread.__init__(self)
        self.start()

    def run(self):
        server_address = ('', self._port)
        server = HTTPServer(server_address, OANHttpHandler)
        while self._running:
            server.handle_request()

    def shutdown(self):
        self._running = False
        r = requests.get('http://localhost:%s' % self._port)
        self.join()
        if r.status_code == 200:
            return True
        else:
            return False

# server = OANHTTPServer(8000)
# sleep(10)
# server.shutdown()



# while True:
#     sleep(100000)
