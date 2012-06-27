#!/usr/bin/env python



import requests
from time import sleep
from threading import Thread, Event
import sys

import zmq
import random

from oan.util.daemon_base import OANDaemonBase
from oan.util.signal_handler import OANSignalHandler, OANTerminateInterrupt
from test.test_case import OANTestCase

# Files used in test.
F_PID="/tmp/ut_zeromq_daemon%s.pid"
F_OUT="/tmp/ut_zeromq_daemon%s.out"
F_ERR="/tmp/ut_zeromq_daemon%s.err"
F_DWN="/tmp/ut_zeromq_daemon%s.down"


class ZeroController:

    controller = None
    running = None

    _event = Event()

    @staticmethod
    def start(context):
        ZeroController._event.clear()
        ZeroController.running = True
        ZeroController.controller = context.socket(zmq.PUB)
        ZeroController.controller.bind('inproc://controller')

    @staticmethod
    def sleep(sec):
        ZeroController._event.wait(sec)

    @staticmethod
    def shutdown():
        ZeroController.running = False
        ZeroController._event.set()
        ZeroController.controller.send('command shutdown 1')
        ZeroController.controller.close()

class ZeroSever:

    _shutdown = False
    _thread = None

    @staticmethod
    def start(context, port):
        ZeroSever._thread = Thread(target=ZeroSever.run, kwargs={
            'port' : port, 'context' : context})
        ZeroSever._thread.name="ZeroServer"
        ZeroSever._thread.start()

    @staticmethod
    def run(context, port):
        """Servern send out values to all connected sockets"""

        socket = context.socket(zmq.PUB)
        socket.bind("tcp://*:%d" % port)
        print "Server listen on ... %d" % port

        while ZeroController.running:
            val1 = random.randrange(0,200)
            val2 = random.randrange(200,250)
            socket.send("%d %d %d" % (port, val1, val2))
            ZeroController.sleep(1)

        # all messages that is not sent will be destroyed
        socket.setsockopt(zmq.LINGER, 0)
        socket.close()

class ZeroClient:

    _shutdown = False
    _thread = None

    @staticmethod
    def start(context, ports):
        ZeroClient._thread = Thread(target=ZeroClient.run, kwargs={
            'ports' : ports, 'context' : context})
        ZeroClient._thread.name="ZeroClient"
        ZeroClient._thread.start()


    @staticmethod
    def run(context, ports):

        print "Subscibe to controller"
        controller = context.socket(zmq.SUB)
        controller.connect('inproc://controller')
        controller.setsockopt(zmq.SUBSCRIBE, "")

        #  Socket to talk to server, one zero socket is connected
        # to all servers.
        socket = context.socket(zmq.SUB)

        for p in ports:
            print "Subscibe to node on port %s" % p
            socket.connect ("tcp://localhost:%s" % p)

        socket.setsockopt(zmq.SUBSCRIBE, "")

        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        poller.register(controller, zmq.POLLIN)

        while ZeroController.running:
            try:
                socks = dict(poller.poll(-1))
                if controller in socks and socks[controller] == zmq.POLLIN:
                    command = controller.recv()
                    print "Command from controller [%s] " % command
                    del command

                if socket in socks and socks[socket] == zmq.POLLIN:
                    message = socket.recv()
                    port, val1, val2 = message.split()
                    print "Message from port %s (%s+%s=%d)" % (
                          port, val1, val2, int(val1) + int(val2))

                    del message

                sys.stdout.flush()

            except zmq.ZMQError:
                print "What!"

        # all messages that is not sent will be destroyed
        socket.setsockopt(zmq.LINGER, 0)
        socket.close()

        controller.setsockopt(zmq.LINGER, 0)
        controller.close()

class TestDaemon(OANDaemonBase):
    port = None

    def run(self):

        # just create one context
        context = zmq.Context()
        ZeroController.start(context)
        ZeroSever.start(context, self.port)
        ZeroClient.start(context, range(8000, 8001))

        try:
            OANSignalHandler.wait()
        except OANTerminateInterrupt:
            ZeroController.shutdown()
        finally:
            print "stop: ", self.port
            f=open(F_DWN % self.port, "w")
            f.write("shutdown")
            f.close()

class TestZeroMqServer(OANTestCase):
    _daemon = None

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_multi_deamon(self):
        daemon=[]
        for port in range(8000, 8001):
            d = TestDaemon(F_PID % port, stdout=F_OUT % port, stderr=F_ERR % port)
            d.port = port
            d.start()
            daemon.append(d)

        sleep(20)

        for d in daemon:
            d.stop()
