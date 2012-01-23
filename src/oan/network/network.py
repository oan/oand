#!/usr/bin/env python
'''
network thread that handles all the network traffic

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import asyncore
import socket
import time
import thread
import threading
from datetime import datetime, timedelta
from Queue import Queue
from threading import Thread

from oan.util import log
from oan.event import OANEvent
from server import OANServer
from oan.event import OANEvent
from oan.passthru import OANPassthru
from oan.message import OANMessageShutdown

class OANTimer(object):
    checked = None
    expires = None
    callback = None
    interval = None

    def __init__(self, sec, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.interval = sec
        self.later(self.interval)


    def later(self, sec):
        self.expires = datetime.utcnow() + timedelta(seconds = sec)

    def check(self):
        self.checked = datetime.utcnow()
        if (self.expires < self.checked):
            self.callback(*self.args, **self.kwargs)
            self.later(self.interval)
            return True

        return False



'''


'''
class OANNetworkMessageListen:
    port = None

    @classmethod
    def create(cls, port):
        obj = cls()
        obj.port = port
        return obj

    def execute(self, server):
        log.info("OANNetworkMessageListen")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("google.com",80))
        host = s.getsockname()[0]
        s.close()

        server.start_listen(host, self.port)


'''

'''
class OANNetworkMessageConnectOan:
    host = None
    port = None

    @classmethod
    def create(cls, host, port):
        obj = cls()
        obj.host = host
        obj.port = port
        return obj

    def execute(self, server):
        log.info("OANNetworkMessageConnectOan")
        server.connect_to_oan(self.host, self.port)


'''

'''
class OANNetworkMessageShutdown:
    def execute(self, server):
        pass

class OANNetworkWorker(Thread):


    # === Event === #
    on_bridge_added = None
    on_bridge_removed = None
    on_bridge_idle = None

    # === Private === #
    _timers = None
    _pass = None
    _started = None


    def __init__(self, passthru):
        Thread.__init__(self)
        self._pass = passthru
        self._timers = []
        self._started = threading.Event()
        Thread.start(self)
        self._started.wait()


    def add_timer(self, timer):
        self._timers.append(timer)


    def remove_timer(self, timer):
        self._timers.remove(timer)


    '''
    move to messages instead

    def listen(self, node):
        self.add_call(self._server.start_listen, node)

    def connect_to_node(self, node):
        self.add_call(self._server.connect_to_node, node)

    def connect_to_oan(self, host, port):
        self.add_call(self._server.connect_to_oan, host, port)
    '''

    def run(self):
        q = self._pass
        server = OANServer()
        self.on_bridge_added = server.on_bridge_added
        self.on_bridge_removed = server.on_bridge_removed
        self.on_bridge_idle = server.on_bridge_idle

        log.info("Start network worker %s" % self.name)
        self._started.set()

        while True:
            asyncore.loop(0.1, False, None, 10)

            for timer in self._timers:
                timer.check()

            if not q.empty():
                (message, back) = q.get()
                try:
                    ret = message.execute(server)
                    self._pass.result(ret, back)
                except Exception as ex:
                    self._pass.error(message, ex, back)

                if isinstance(message, OANNetworkMessageShutdown):
                    break

        server.shutdown()
        asyncore.loop()
        log.info("Stop network worker %s" % self.name)


class OANNetwork:

    # === Public === #
    config = None

    # === Event === #
    on_message = None
    on_error = None
    '''
        use:
        def my_bridge_added(bridge)
            pass

        on_bridge_added += (my_bridge_added, )
    '''
    on_bridge_added = None

    '''
        use:
        def my_bridge_removed(bridge)
            pass

        on_bridge_removed += (my_bridge_removed, )
    '''
    on_bridge_removed = None


    '''
        use:
        def my_bridge_idle(bridge)
            pass

        on_bridge_idle += (my_bridge_idle, )
    '''
    on_bridge_idle = None


    # === Private === #
    _worker = None
    _pass = None

    def __init__(self, config):
        self._pass = OANPassthru()
        self._worker = OANNetworkWorker(self._pass)
        self.on_message = self._pass.on_message
        self.on_error = self._pass.on_error
        self.on_bridge_added = self._worker.on_bridge_added
        self.on_bridge_removed = self._worker.on_bridge_removed
        self.on_bridge_idle = self._worker.on_bridge_idle

    def add_timer(self, timer):
        self._worker.add_timer(timer)

    def remove_timer(self, timer):
        self._worker.remove_timer(timer)

    def execute(self, message):
        self._pass.execute(message)

    def select(self, message):
       return self._pass.select(message)

    def get(self, message):
        for ret in self._pass.select(message):
            return ret

    def shutdown(self):
        self._pass.execute(OANNetworkMessageShutdown())
        self._worker.join()
