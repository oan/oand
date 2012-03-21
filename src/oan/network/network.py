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

import asyncore
from time import sleep
from Queue import Empty
from datetime import datetime, timedelta
from threading import Thread

from oan.util import log
from oan.passthru import OANPassthru
from oan.util.thread import OANThread
from oan.util.throttle import OANThrottle

from oan.network.bridge import OANBridge
from oan.network.server import OANListen

from oan.manager import node_manager, dispatcher
from oan.network.network_node import OANNetworkNodeState
from uuid import UUID

class OANNetworkTimer(object):
    """
    Execute a callback function every X seconds.

    check() should be executed every second to be able to internally execute
    callbacks that has an expired timer.

    """
    _interval = None
    _callback = None
    _args = None
    _kwargs = None

    _expires = None

    def __init__(self, sec, callback, *args, **kwargs):
        self._interval = sec
        self._callback = callback
        self._args = args
        self._kwargs = kwargs

        self._calc_expire()

    def check(self):
        """Execute callback if the timer has expired."""
        checked = datetime.utcnow()
        if (self._expires < checked):
            self._callback(*self._args, **self._kwargs)
            self._calc_expire()

    def _calc_expire(self):
        """Calculate and set the next time the cmd should be executed."""
        self._expires = datetime.utcnow() + timedelta(seconds = self._interval)

class TestOanNetworkServer:

    def test_connected(self):
        pass

    def test_send(self):
        oan_ids = [UUID(""), UUID()]
        message = TestMessage.create()
        OANNetworkServer.send(oan_ids, message)
        mock_dispatcher


    def test_max_concurrent(self):
        pass


class OANNetworkServer:

    _auth = None

    """ tuple ((host, port), [messages]) """
    _out = {}

    """ connected bridges """
    _bridges = {}

    """ max concurrent open bridges """
    _concurrent_bridges = 10

    @staticmethod
    def send(oan_ids, message):

        for oan_id in oan_ids:
            log.debug("OANNetworkServer: oan_id: %s, message: %s" % (oan_id, str(message)))
            node = node_manager.get_node(oan_id)
            if node is not None:
                if node.is_blocked() and OANNetworkServer._auth.blocked:
                    self._relay_to_node(oan_id, message)
                else:
                    self._send_to_node(node, message)
            else:
                log.info("OANNetworkServer:Error node is missing %s" % oan_id)


    @staticmethod
    def connect(host, port, auth):
        bridge = OANBridge(host, port, auth)
        bridge.connect_callback = OANNetworkServer.bridge_connected
        bridge.message_callback = OANNetworkServer.bridge_message
        bridge.close_callback = OANNetworkServer.bridge_closed
        bridge.error_callback = OANNetworkServer.bridge_error
        bridge.connect()

    @staticmethod
    def listen(auth):
        listen = OANListen(auth)
        listen.accept_callback = OANNetworkServer.bridge_accepted
        listen.start()

    @staticmethod
    def bridge_connected(bridge, auth):
        log.info("OANNetworkServer: bridge_connected %s" % bridge)

        node = node_manager().create_node(
            UUID(auth.oan_id), auth.host, auth.port, auth.blocked
        )
        node.touch()
        bridge.node = node
        bridge.out_queue = node.out_queue

    @staticmethod
    def bridge_closed(bridge):
        log.info("OANNetworkServer: bridge_closed %s" % bridge)
        if bridge.node is not None:
            bridge.node.update(state = OANNetworkNodeState.DISCONNECTED)
        pass

    @staticmethod
    def bridge_error(bridge, exc_type, exc_value):
        log.info("OANNetworkServer: bridge_error %s" % bridge)
        pass

    @staticmethod
    def bridge_accepted(bridge):
        log.info("OANNetworkServer: bridge_accepted %s" % bridge)
        bridge.connect_callback = OANNetworkServer.bridge_connected
        bridge.message_callback = OANNetworkServer.bridge_message
        bridge.close_callback = OANNetworkServer.bridge_closed
        bridge.error_callback = OANNetworkServer.bridge_error
        pass

    @staticmethod
    def bridge_message(bridge, message):
        log.info("OANNetworkServer: bridge_message %s" % bridge)
        dispatcher().execute(message)
        pass



class OANNetworkWorker(OANThread):
    """
    Handles the main network loop.

    Polls the network passthru queue for new commands/messages that needs
    to be executed.

    Polls the network queue through asyncore for new connections and sends
    them internally in asyncore code to the OANListen object.

    Controll if OANNetworkTimer callbacks should be executed.

    """

    # Private variables
    _timers = None
    _pass = None

    def __init__(self, passthru):
        OANThread.__init__(self)
        self.name = "NETW-" + self.name.replace("Thread-", "")

        self._pass = passthru
        self._timers = []
        Thread.start(self)

    def add_timer(self, timer):
        """Add a OANNetworkTimer to be executed by the main network loop."""
        self._timers.append(timer)

    def remove_timer(self, timer):
        """Remove a OANNetworkTimer from the main network loop."""
        self._timers.remove(timer)

    def run(self):
        """Main network loop"""
        q = self._pass
        log.info("Start network worker %s" % self.name)

        while True:
            self.enable_shutdown()
            asyncore.loop(60, True, None, 1)
            self.disable_shutdown()

            for timer in self._timers:
                timer.check()

            try:
                while True:
                    (message, back) = q.get(True, 0.5 + OANThrottle.calculate(0.2))
                    try:
                        ret = message.execute()
                        self._pass.result(ret, back)
                    except Exception as ex:
                        self._pass.error(message, ex, back)

            except Empty:
                pass

            except Exception, e:
                print e
                sleep(5)

class OANNetwork:
    """
    Handle communication between nodes through commands and messages.

    EVENTS:

    on_message  Callback event that will be triggered when a message is poped
                from the queue.

                Example:
                def got_message(self, message):
                    print "got message"

                on_message.append(got_message)


    on_error    Callback event that will be called when worker thread got
                any error, for example when the message execute raises an
                exception.

                Example:
                def got_error(self, message, exception):
                    print "got error", exception

                on_error.append(got_error)

    """
    # Events
    on_message = None
    on_error = None

    # TODO: Not implemented.
    #on_receive = None
    #on_send = None

    # Private variables

    # Will only have one worker because only one asyncore.loop can exist.
    _pass = None
    _worker = None

    def __init__(self):
        self._pass = OANPassthru()
        self._worker = OANNetworkWorker(self._pass)
        self.on_message = self._pass.on_message
        self.on_error = self._pass.on_error

    def add_timer(self, timer):
        """Add a OANNetworkTimer to be executed by the main network loop."""
        self._worker.add_timer(timer)

    def remove_timer(self, timer):
        """Remove a OANNetworkTimer from the main network loop."""
        self._worker.remove_timer(timer)

    def execute(self, command):
        """Execute a command via worker thread."""
        self._pass.execute(command)

    def select(self, command):
        """Execute a command via worker thread, return yielded result."""
        return self._pass.select(command)

    def get(self, command):
        """Execute a command via worker thread, return first row of result."""
        for ret in self._pass.select(command):
            return ret

    def shutdown(self):
        """OANNetworkWorker is a deamon thread so just wait for it to die"""
        self._worker.join()
        return True
