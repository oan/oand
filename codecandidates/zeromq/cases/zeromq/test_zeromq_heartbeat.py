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
from oan.heartbeat import OANHeartbeat
from oan.network import serializer
from test.test_case import OANTestCase

# Files used in test.
F_PID="/tmp/ut_zeromq_daemon%s.pid"
F_OUT="/tmp/ut_zeromq_daemon%s.out"
F_ERR="/tmp/ut_zeromq_daemon%s.err"
F_DWN="/tmp/ut_zeromq_daemon%s.down"


"""

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

class ZeroMessageReady:
    oan_id = None
    host = None
    port = None

    def __init__(self, oan_id = None, host = None, port = None):
        self.oan_id = oan_id
        self.host = host
        self.port = port

    def execute(self):
        if (self.oan_id not in ZeroNodeManager.nodes)
            node = ZeroNode(self.oan_id, self.host, self.port)
            ZeroNodeManager.nodes[self.oan_id] = node
        else
            node = ZeroNodeManager.nodes[self.oan_id]
            node.host = self.host
            node.port = self.port

        node.heartbeat.touch()
        print node.heartbeat

serializer.add(ZeroMessageReady)

class ZeroResource:

    _values = None
    _hashes = None
    _hash = None

    def __init__(self):
        self._values = {}
        self._hashes = []
        self._hash = hash(tuple(self._hashes))

    def add(self, key, entry):
        if key not in self._values:
            self._values[key] = []

        if entry not in self._values[key]:
            self._values[key].append(entry)
            self._hashes.append(hash(entry))
            self._hash = hash(tuple(sorted(self._hashes)))
            return True

        return False

    def put(self, key, value):
        return self.add(key, (time(), value))

    def get(self, key):
        pass

    def hash(self):
        return self._hash


class ZeroConnections:
    connections = None
    port = None

    def __init__(self, port, start, stop):
        self.port = port
        self.connections = self._get_connections(start, stop)

    def _add_connection(self, idx, connections):
        if idx not in connections:
            connections.append(idx)

    def _get_connections(self, start, stop):
        ret = []

        # before
        #for i in range(1, 2):
        #    if self.port-i < start:
        #        self._add_connection(stop - i, ret)
        #    else:
        #       self._add_connection(self.port - i, ret)

        # after
        for i in range(1, 2):
            if self.port + i > stop:
                self._add_connection(start - 1 + i, ret)
            else:
                self._add_connection(self.port + i, ret)

        # far away
        far = self.port - 1 + (stop - start) / 2
        for i in range(1, 2):
            if far + i >= stop:
                self._add_connection(start + far - stop + i, ret)
            else:
                self._add_connection(far + i, ret)

        return ret



class ZeroStatistic:
    read_count = 0
    send_count = 0
    read_bytes = 0
    send_bytes = 0

class ZeroResourceManager:
    resources = {}

class ZeroNodeManager:
    nodes = {}

class ZeroNode
    oan_id = None
    heartbeat = None
    host = None
    port = None

    def __init__(self, oan_id, host = None, port = None):
        self.oan_id = oan_id
        self.host = host
        self.port = port
        self.heartbeat = OANHeartbeat()

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
        ZeroController.controller.send('command shutdown')
        ZeroController.controller.close()

class ZeroServer:

    _shutdown = False
    _thread = None
    _out = None
    _push = None
    _ready = None

    @staticmethod
    def start(context, port, node):
        ZeroServer._out = Queue()
        ZeroServer._push = Queue()
        ZeroServer._ready = {}
        ZeroServer._thread = Thread(target=ZeroServer.run, kwargs={
            'context' : context,
            'port' : port,
            'node' : node
        })
        ZeroServer._thread.name="ZeroServer"
        ZeroServer._thread.start()

    @staticmethod
    def send(oan_id, message):
        ZeroServer._out.put((oan_id, message))

    @staticmethod
    def push(message):
        ZeroServer._push.put(message))

    @staticmethod
    def shutdown():
        ZeroServer._out.put((None, None))

    @staticmethod
    def run(context, port, node):
        """Servern send out values to all connected sockets"""

        socket = context.socket(zmq.ROUTER)
        socket.bind("tcp://*:%d" % port)
        print "Server listen on ... %d" % port
        while True:
            incomming = socket.recv_multipart()
            in_oan_id = incomming[0]
            in_message = serializer.decode(incomming[2])
            in_message.execute()

            oan_id, message = ZeroServer._out.get()
            if message is None:
                print "shutdown"
                break

            outgoing = [oan_id, "", message]
            socket.send_multipart(outgoing)

            ZeroStatistic.send_count += 1
            ZeroStatistic.send_bytes += len(message)

        # all messages that is not sent will be destroyed
        socket.setsockopt(zmq.LINGER, 0)
        socket.close()

class ZeroClient:

    _shutdown = False
    _thread = None
    _auth = None

    @staticmethod
    def start(context, auth, ports):
        ZeroClient._thread = Thread(target=ZeroClient.run, kwargs={
            'auth' = auth, 'ports' : ports, 'context' : context})
        ZeroClient._thread.name="ZeroClient"
        ZeroClient._thread.start()


    @staticmethod
    def run(context, auth, ports):

        print "Subscibe to controller"
        controller = context.socket(zmq.SUB)
        controller.connect('inproc://controller')
        controller.setsockopt(zmq.SUBSCRIBE, "")

        #  Socket to talk to server, one zero socket is connected
        # to all servers.
        socket = context.socket(zmq.REQ)

        for p in ports:
            print "Subscibe to node on port %s" % p
            socket.connect ("tcp://localhost:%s" % p)

        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        poller.register(controller, zmq.POLLIN)

        ready = serializer.encode(ZeroMessageReady(auth)
        while ZeroController.running:
            try:
                socket.send()

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

    def run(self):

        # just create one context
        context = zmq.Context()
        conns = ZeroConnections(self.port, self.port_start, self.port_stop)

        ZeroResourceManager.resources["nodes://"] = ZeroResource()
        ZeroResourceManager.resources["nodes://"].put(str(self.port), "localhost:%s" % self.port)

        #if (self.port == 8000):
        #    resource = ZeroResource()
        #    d = ZeroDirectory("/Users/martinpalmer/Documents/oan/oand/src/oan/database")
        #    for f in d.files:
        #        resource.put(f, "True")

        #    ZeroResourceManager.resources["file://"] = resource

        ZeroController.start(context)
        ZeroServer.start(context, self.port)
        ZeroClient.start(context, conns.connections)

        try:
            while True:
                print "--- dump begin ---"
                for resource_key, resource in ZeroResourceManager.resources.items():
                    print "%s hash:%s" % (resource_key, resource.hash())

                    print "statistic send:[%sc, %sb], read:[%sc, %sb]" % (
                        ZeroStatistic.send_count * len(conns.connections),
                        ZeroStatistic.send_bytes * len(conns.connections),
                        ZeroStatistic.read_count,
                        ZeroStatistic.read_bytes)

                    for vals in sorted(resource._values.values()):
                        for t, val in vals:
                            print "* %s" % (val)

                    try:
                        f = open('/tmp/%s.txt' % self.port, 'r')
                        content = f.read()
                        f.close()
                        ZeroResourceManager.resources["nodes://"].put(str(self.port), content)
                    except Exception, e:
                        print "file error", e

                    ZeroServer.send("%shash %s" % (resource_key, resource.hash()))

                print "--- dump end ---"

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
    _daemon = None

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_multi_deamon(self):
        daemon=[]
        port_start = 8000
        port_stop = 8300

        for port in range(port_start, port_stop):
            d = TestDaemon(F_PID % port, stdout=F_OUT % port, stderr=F_ERR % port)
            d.port = port
            d.port_start = port_start
            d.port_stop = port_stop
            d.start()
            daemon.append(d)

        sleep(1*60*60)

        for d in daemon:
            d.stop()

    def test_get_connections(self):
        for port in range(8000, 8010):
            log.info("%s => %s" % (port , str(ZeroConnections(port, 8000, 8100).connections)))


