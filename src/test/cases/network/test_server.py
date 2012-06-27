import time
import os

from struct import *

from oan.util.daemon_base import OANDaemonBase
from oan.util.signal_handler import OANTerminateInterrupt

from oan.network.server import OANAuth, OANServer, OANNetworkError, OANCounter, OANLogCounter
from oan.util import log
from oan.util.queue import OANQueue
from test.test_case import OANTestCase

class ServerDaemon(OANDaemonBase):
    auth = None

    def run(self):
        try:
            log.info("ServerDaemon::run::begin")

            self.auth = OANAuth(
                'oand v1.0', '00000000-0000-code-8000-000000000000',
                'localhost', 8000, False
            )

            OANServer.connect_callback = self.my_test_connected
            OANServer.close_callback = self.my_test_closed
            OANServer.message_callback = self.my_test_message
            OANServer.start(self.auth)

            log.info("ServerDaemon::run::end")
            self.wait()

        except OANTerminateInterrupt:
            OANServer.shutdown()

    def my_test_connected(self, auth):
        log.info("ServerDaemon::my_test_connected")

    def my_test_closed(self, auth, message):
        log.info("ServerDaemon::my_test_connected")

    def my_test_message(self, url, messages):
        log.info("ServerDaemon::my_test_messages %s" % len(messages))
        OANServer.push([url], messages)


class TestOanSocket(OANTestCase):
    daemon = None
    auth = None
    start = None

    def setUp(self):
        self.daemon = ServerDaemon(
            "/tmp/ut_socket.pid", stdout='/tmp/ut_socket_out.log',
            stderr='/tmp/ut_socket_err.log')

        self.daemon.start()

        self.reset_all_counters()
        self.auth = OANAuth("OAN v0.1", '00000000-0000-code-8001-000000000000', "localhost", 8001, False)
        OANServer.connect_callback = self.my_test_connected
        OANServer.close_callback = self.my_test_closed
        OANServer.start(self.auth)

        self.start = time.time()

    def tearDown(self):

        elapsed = (time.time() - self.start)
        (utime, stime, cutime, cstime, elapsed_time) = os.times()
        log.info("Stat: %s, %s, %s, %s, %s" % (utime, stime, cutime, cstime, elapsed_time))

        if elapsed > 0:
            log.info("sec[%s] avg[%s] in[%s][%s KB] out[%s][%s KB] speed[%s MB/S]" % (
                elapsed, (OANCounter.in_count / elapsed),
                OANCounter.in_count, OANCounter.in_bytes / 1000,
                OANCounter.out_count, OANCounter.out_bytes / 1000,
                OANCounter.out_bytes / elapsed / 1000000)
            )


        log.info(OANLogCounter.result())

        OANServer.shutdown()
        self.daemon.stop()

    def my_test_connected(self, auth):
        log.info("my_test_connected")
        self.inc_counter('my_test_connected')
        log.info(self.assert_counters)

    def my_test_closed(self, auth, messages):
        log.info("my_test_closed")
        self.inc_counter('my_test_closed')
        log.info(self.assert_counters)

    def my_test_message(self, auth, message):
        pass

    def my_test_error(self, auth, error):
        pass

    def atest_failed_start(self):
        # test start with same port
        auth = OANAuth("OAN v0.1", "oan:1", "localhost", 8001, False)

        with self.assertRaises(OANNetworkError):
            OANServer.start(auth)

        # test start with another port
        auth = OANAuth("OAN v0.1", "oan:1", "localhost", 8002, False)

        with self.assertRaises(OANNetworkError):
            OANServer.start(auth)

    def atest_failed_shutdown(self):

        # shutdown the server that is started in setup
        OANServer.shutdown()

        with self.assertRaises(OANNetworkError):
            OANServer.shutdown()

        # start the server so it can be shitdown in tearDown
        OANServer.start(self.auth)

    def atest_failed_connect(self):
        with self.assertRaises(OANNetworkError):
            OANServer.connect([("localhost", 8002)])

    def test_connect(self):
        OANServer.connect([("localhost", 8000)])
        self.assert_counter_wait('my_test_connected', 1)

    def atest_multi_connect(self):
        auth = OANAuth("OAN v0.1", "oan:1", "localhost", 8001, False)

        OANServer.connect([("localhost", 8000)])
        OANServer.connect([("localhost", 8000)])
        OANServer.connect([("localhost", 8000)])
        OANServer.connect([("localhost", 8000)])
        OANServer.connect([("localhost", 8000)])

    my_queue = OANQueue()
    def got_message(self, url, messages):
        self.my_queue.put(messages)

    def atest_server(self):

        num_push = 100
        num_clients = 1
        to_push = ["M" * 500]
        clients = []

        OANServer.message_callback = self.got_message

        start = time.time()

        for x in xrange(0,num_clients):
            OANServer.connect([("localhost", 8000)])

            for x in xrange(0,num_push):
                OANServer.push([("localhost", 8000)], to_push)
                #time.sleep(0.00001)

        excepted = num_push * num_clients * len(to_push)
        c = 0
        while c < excepted:
            c += len(self.my_queue.get())

        elapsed = (time.time() - start)
        (utime, stime, cutime, cstime, elapsed_time) = os.times()

        log.info("sec[%s] avg[%s] in[%s][%s KB] out[%s][%s KB] speed[%s MB/S]" % (
            elapsed, (c / elapsed),
            OANCounter.in_count, OANCounter.in_bytes / 1000,
            OANCounter.out_count, OANCounter.out_bytes / 1000,
            OANCounter.out_bytes / elapsed / 1000000)
        )

        log.info("Stat: %s, %s, %s, %s, %s" % (utime, stime, cutime, cstime, elapsed_time))

        log.info(OANLogCounter.result())



