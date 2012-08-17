# encoding: utf-8
#
#   Custom routing Router to Mama (ROUTER to REQ)
#
#   Author: Jeremy Avnet (brainsik) <spork(dash)zmq(at)theory(dot)org>
#

import time
import random
from threading import Thread
from Queue import Queue, Empty

import zmq


from oan.util import log
from test.test_case import OANTestCase


# Cross-connected ROUTER sockets addressing each other
#
# Author: Lev Givon <lev(at)columbia(dot)edu>

import zmq
import time


class ZeroConnection:

    socket = None

    def __init__(self, context, url, oan_id, bind = False):
        if bind:
            self.socket = context.socket(zmq.ROUTER)
            self.socket.setsockopt(zmq.IDENTITY, oan_id)
            self.socket.bind(url)
            log.info("bind to %s " % url )
        else:
            self.socket = context.socket(zmq.ROUTER)
            self.socket.setsockopt(zmq.IDENTITY, oan_id)
            self.socket.connect(url)
            log.info("connect to %s " % url)

class ZeroRouter(Thread):

    context = None
    url = None
    oan_id = None
    bind = None

    _out = None

    def __init__(self, context, url, oan_id, bind = False):
        Thread.__init__(self)
        self.context = context
        self.url = url
        self.oan_id = oan_id
        self.bind = bind
        self._out = Queue()

    def send(self, oan_id, message):
        self._out.put((oan_id, message))

    def run(self):
        conn = ZeroConnection(self.context, self.url, self.oan_id, self.bind)
        socket = conn.socket

        #poller = zmq.Poller()
        #poller.register(socket, zmq.POLLIN)

        while True:
            try:
                oan_id, message = self._out.get(True, 1)
                log.info("try Send %s to %s" % (message, oan_id))
                socket.send_multipart([oan_id, "", message])
                log.info("Send %" % message)
            except Empty:
                log.info("Empty")
            except Exception, e:
                log.info("Error %s" % str(e))

            #socks = dict(poller.poll(1000))

            #if socket in socks and socks[socket] == zmq.POLLIN:
            #    recv_message = socket.recv_multipart()
            #    log.info("Recv %s" % recv_message)



#server.send_multipart(["WORKER", "", "server to worker"])
#zhelpers.dump(worker)

#worker.send_multipart(["SERVER", "", "send to server"])
#zhelpers.dump(server)

class TestZeroRouter(OANTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def atest_connect_to_bind(self):

        context = zmq.Context()
        r1 = ZeroRouter(context, "tcp://*:8001", "r1", True)
        r2 = ZeroRouter(context, "tcp://localhost:8001", "r2", False)

        r1.start()
        r2.start()

        for x in xrange(1,10):
            r1.send(r1, "Hello from r1 [%s]" % x)
            time.sleep(1)

        for x in xrange(1,10):
            log.info(r1.recv_multipart())


    def client(self, context, port, connect_to):


    def router(self, context, port, connect_to):
        r = context.socket(zmq.ROUTER)
        r.setsockopt(zmq.IDENTITY, "r%s" % port)
        r.setsockopt(zmq.HWM, 5)
        r.bind("tcp://*:%s" % port)
        r.bind("inproc://router:%s" % port)

        soc = context.socket(zmq.ROUTER)
        soc.setsockopt(zmq.IDENTITY, "r%s" % port)
        soc.setsockopt(zmq.HWM, 5)
        for connect_port in connect_to:
            soc.connect("tcp://localhost:%s" % connect_port)

        poller = zmq.Poller()
        poller.register(r, zmq.POLLIN)

        x = 0
        while True:

            socks = dict(poller.poll(0.1))

            if r in socks and socks[r] == zmq.POLLIN:
                msg = r.recv_multipart()
                if (x % 10000 == 0):
                    log.info(msg)

            if soc in socks and socks[soc] == zmq.POLLIN:
                msg = soc.recv_multipart()
                if (x % 10000 == 0):
                    log.info(msg)

            for connect_port in connect_to:
                soc.send_multipart(["r%s" % connect_port, "", "%s => %s [%s]" % (port, connect_port, x) ])

            x += 1
            #time.sleep(0.01)


    def connect(self, context, ports):
        r2 = context.socket(zmq.ROUTER)
        for connect_port in ports:
            r2.connect("tcp://localhost:%s" % connect_port)

        poller = zmq.Poller()
        poller.register(r2, zmq.POLLIN)

        x = 0
        while True:

            socks = dict(poller.poll(1000))

            if r2 in socks and socks[r2] == zmq.POLLIN:
                log.info(r2.recv_multipart())

            for connect_port in ports:
                r2.send_multipart(["r%s" % connect_port, "", "%s => %s [%s]" % ("unknown", connect_port, x) ])

            x += 1
            time.sleep(1)


    def bind(self, context, port):
        r1 = context.socket(zmq.ROUTER)
        r1.setsockopt(zmq.IDENTITY, "r%s" % port)
        r1.bind("tcp://*:%s" % port)

        poller = zmq.Poller()
        poller.register(r1, zmq.POLLIN)

        x = 0
        while True:

            socks = dict(poller.poll(1000))

            if r1 in socks and socks[r1] == zmq.POLLIN:
                msg = r1.recv_multipart()
                log.info(msg)
                r1.send_multipart([msg[0], "", "%s to %s [%s]" % (port, msg[0], x) ])

            x += 1
            time.sleep(0.1)



    def listen_echo(self, context, oan_id, port):
        r = context.socket(zmq.ROUTER)
        r.setsockopt(zmq.IDENTITY, oan_id)
        r.bind("tcp://*:%s" % port)

        poller = zmq.Poller()
        poller.register(r, zmq.POLLIN)

        while True:
            socks = dict(poller.poll(-1))

            if r in socks and socks[r] == zmq.POLLIN:
                msg = r.recv_multipart()
                log.info(msg)
                r.send_multipart(msg)


    def connect_echo(self, context, oan_id, port):
        r = context.socket(zmq.REQ)
        r.setsockopt(zmq.IDENTITY, oan_id)
        r.connect("tcp://localhost:%s" % port)

        log.info("send handshake")
        r.send("handshake 1 2")
        log.info(r.recv())

        while True:
            r.send("kalle 1 2")
            log.info(r.recv())
            time.sleep(1)


    def atest_echo_req_router(self):
        context = zmq.Context()

        t = Thread(target=self.listen_echo, kwargs={
            'context' : context,
            'oan_id' : "o1",
            'port' : 8000,
        })

        t.name="o1"
        t.start()


        t = Thread(target=self.connect_echo, kwargs={
            'context' : context,
            'oan_id' : "o2",
            'port' : 8000,
        })

        t.name="o2"
        t.start()


    def atest_router_router(self):
        # Cross-connected ROUTER sockets addressing each other
        #
        # Author: Lev Givon <lev(at)columbia(dot)edu>

        context = zmq.Context()

        t = Thread(target=self.bind, kwargs={'context' : context, 'port' : 8000})
        t.name="r1"
        t.start()

        t = Thread(target=self.connect, kwargs={'context' : context, 'ports' : [8000]})
        t.name="r2"
        t.start()


    def test_router_router(self):
        # Cross-connected ROUTER sockets addressing each other
        #
        # Author: Lev Givon <lev(at)columbia(dot)edu>

        context = zmq.Context()

        #t = Thread(target=self.bind, kwargs={'context' : context})
        #t.name="r1"
        #t.start()

        #t = Thread(target=self.connect, kwargs={'context' : context})
        #t.name="r2"
        #t.start()

        t = Thread(target=self.router, kwargs={
            'context' : context,
            'port' : 8000,
            'connect_to' : [8000]
        })

        t.name="r8000"
        t.start()


        t = Thread(target=self.router, kwargs={
            'context' : context,
            'port' : 8001,
            'connect_to' : [8003]
        })

        t.name="r8001"
        t.start()


