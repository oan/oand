#!/usr/bin/env python
'''
RPC server handling request from oan clients.

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
from Queue import Queue
from threading import Thread
from oan_bridge import OANBridge


class OANEvent(list):
    """Event subscription.

    A list of callable objects. Calling an instance of this will cause a
    call to each item in the list in ascending order by index.

    Example Usage:
    >>> def f(x):
    ...     print 'f(%s)' % x
    >>> def g(x):
    ...     print 'g(%s)' % x
    >>> e = Event()
    >>> e()
    >>> e.append(f)
    >>> e(123)
    f(123)
    >>> e.remove(f)
    >>> e()
    >>> e += (f, g)
    >>> e(10)
    f(10)
    g(10)
    >>> del e[0]
    >>> e(2)
    g(2)

    """
    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)

    def __repr__(self):
        return "Event(%s)" % list.__repr__(self)


class OANLoop(Thread):

    ''' use: loop.on_start += my_loop_start() '''
    on_start = OANEvent()

    ''' use: loop.on_shutdown += my_loop_shutdown() '''
    on_shutdown = OANEvent()

    ''' use: loop.on_stop += my_loop_stop() '''
    on_stop = OANEvent()

    _running = False

    def __init__(self):
        Thread.__init__(self)

    def start(self):
        if (not self._running):
            self._running = True
            Thread.start(self)

    def stop(self):
        self._running = False

    def run(self):
        print "OANLoop: started"
        self.on_start()
        try:
          while(self._running):
                asyncore.loop(1, False, None, 2)
                #print "OANLoop: check if running"
        except KeyboardInterrupt:
            self._running = false

        print "OANLoop: shutdown"
        self.on_shutdown()
        asyncore.loop()
        self.on_stop()
        print "OANLoop stopped"

class OANServer(asyncore.dispatcher):
    bridges = []

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        print "OanServer:handle_accept"
        pair = self.accept()
        if pair is None:
            pass
        else:
            sock, addr = pair
            print 'OanServer: incoming connection from %s' % repr(addr)
            self.bridges.append( OANBridge(sock, Queue(), Queue()) )

    def handle_close(self):
        print "OanServer:handle_close"
        self.close()

    def shutdown(self):
        self.close()
        for bridge in self.bridges:
            bridge.shutdown()

    def handle_error(self):
        print "OanServer:handle_error"
        asyncore.dispatcher.handle_error(self)

def main():
    server = OANServer('localhost', 8080)
    loop = OANLoop()
    #loop.on_shutdown += server.shutdown()
    loop.start()

    time.sleep(10)

    server.bridges[0].out_queue.put("from server 1");
    server.bridges[0].out_queue.put("from server 2");
    server.bridges[0].out_queue.put("from server 3");
    server.bridges[0].out_queue.put("from server 4");
    server.bridges[0].out_queue.put("from server 5");
    server.bridges[0].out_queue.put("from server 6");


if __name__ == "__main__":
    main()
