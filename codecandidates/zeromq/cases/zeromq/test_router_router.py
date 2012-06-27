#!/usr/bin/env python


from time import sleep, time
from threading import Thread, Event
from Queue import Queue
import json

import sys
import os

import zmq
from random import randrange, randint

from oan.util.daemon_base import OANDaemonBase
from oan.util.signal_handler import OANSignalHandler, OANTerminateInterrupt
from oan.util import log
from test.test_case import OANTestCase

# Files used in test.
F_PID="/tmp/ut_zeromq_daemon%s.pid"
F_OUT="/tmp/ut_zeromq_daemon%s.out"
F_ERR="/tmp/ut_zeromq_daemon%s.err"
F_DWN="/tmp/ut_zeromq_daemon%s.down"


"""
q
* snapshot.
  pub-sub
  req-res




* test med node info i files.



* hur bygger vi upp kuben.




* prioriterar att skicka ut hash till andra.
--------------------------


* pub-sub multicast

----------------------
P O P             P
  P O P             P


X => PUB (hash)
SUB => another.hash != my.hash
    SEND my resource(list)





"""

class ZeroServer:

    _shutdown = False
    _thread = None
    _out = None

    @staticmethod
    def start(context, port, connect_to):
        ZeroServer._out = Queue()
        ZeroServer._thread = Thread(target=ZeroServer.run, kwargs={
            'port' : port, 'connect_to': connect_to, 'context' : context})
        ZeroServer._thread.name="ZeroServer"
        ZeroServer._thread.start()

    @staticmethod
    def send(message):
        ZeroServer._out.put(message)

    @staticmethod
    def shutdown():
        ZeroServer._out.put(None)

    @staticmethod
    def run(context, port):
        """Servern send out values to all connected sockets"""
        r = context.socket(zmq.ROUTER)
        r.setsockopt(zmq.IDENTITY, "r%s" % port)
        r.bind("tcp://*:%s" % port)

        poller = zmq.Poller()
        poller.register(r, zmq.POLLIN)

        x = 0
        while True:
            socks = dict(poller.poll(-1))

            if r in socks and socks[r] == zmq.POLLIN:
                msg = r.recv_multipart()
                log.info(msg)

            for connect_port in connect_to:
                r.send_multipart(["r%s" % connect_port, "", "%s => %s [%s]" % (port, connect_port, x) ])

            x += 1

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

                    ZeroStatistic.read_count += 1
                    ZeroStatistic.read_bytes += len(message)

                    idx = message.find(' ')
                    url = message[0:idx]
                    value = message[idx+1:]

                    idx = url.find('//')
                    resource_key = url[0: idx+2]
                    path = url[idx+2:]

                    if (path == 'hash'):
                        if resource_key not in ZeroResourceManager.resources:
                            ZeroResourceManager.resources[resource_key] = ZeroResource()

                        print "Recv-hash: %s [%s]==[%s]" % (url, int(value), ZeroResourceManager.resources[resource_key].hash())

                        if int(value) != ZeroResourceManager.resources[resource_key].hash():
                            ZeroServer.send("%svalue %s" % (resource_key, json.dumps(ZeroResourceManager.resources[resource_key]._values)))

                    elif (path == "value"):
                        resource = json.loads(value)
                        print "Recv-value: %s %s" % (url, resource)
                        forward = ZeroResource()
                        for key, entries in resource.items():
                            for entry in entries:
                                #print "Value: %s => %s" % (key, str(tuple(entry)))
                                tuple_value = tuple(entry)
                                if (ZeroResourceManager.resources[resource_key].add(key, tuple_value)):
                                    forward.add(key, tuple_value)

                        if (len(forward._values) > 0):
                            print "forward-value: %s %s" % (url, forward._values)
                            ZeroServer.send("%svalue %s" % (resource_key, json.dumps(forward._values)))

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
    port_start = None
    port_stop = None
    ports = None

    def run(self):

        context = zmq.Context()
        #conns = ZeroConnections(self.port, self.port_start, self.port_stop)

        #ZeroController.start(context)
        ZeroServer.start(context, self.port, self.ports)
        #ZeroClient.start(context, conns.connections)

        try:
            while True:
                #ZeroServer.send("%shash %s" % ("heartbeat://", "1"))

                OANSignalHandler.activate()
                sleep(15)
                OANSignalHandler.deactivate()

        except OANTerminateInterrupt:
            ZeroServer.shutdown()
            ZeroController.shutdown()
        finally:
            print "stop: ", self.port
            f=open(F_DWN % self.port, "w")
            f.write("shutdown")
            f.close()

class TestZeroMqServer(OANTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_multi_deamon(self):
        daemon=[]

        port = 8000
        d = TestDaemon(F_PID % port, stdout=F_OUT % port, stderr=F_ERR % port)
        d.port = port
        d.ports = [8001]
        d.start()
        daemon.append(d)

        port = 8001
        d = TestDaemon(F_PID % port, stdout=F_OUT % port, stderr=F_ERR % port)
        d.port = port
        d.ports = [8000]
        d.start()
        daemon.append(d)

        sleep(1*60*60)

        for d in daemon:
            d.stop()
