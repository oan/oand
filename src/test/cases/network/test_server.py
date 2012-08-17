import time
import os

from oan.util.daemon_base import OANDaemonBase
from oan.util.signal_handler import OANTerminateInterrupt

from oan.network.server import OANAuth, OANServer, OANNetworkError, OANCounter
from oan.util import log
from oan.util import log_counter

from test.test_case import OANTestCase

class ServerDaemon(OANDaemonBase):
    auth = None

    def run(self):
        try:
            log.info("ServerDaemon::run::begin")

            OANServer.connect_callback = self.my_test_connected
            OANServer.close_callback = self.my_test_closed
            OANServer.message_callback = self.my_test_message
            OANServer.start(self.auth)

            log.info("ServerDaemon::run::end")
            self.wait()

        except OANTerminateInterrupt:
            OANServer.shutdown()
            log.info("ServerDaemon::run::OANTerminateInterrupt")
        except Exception, e:
            log.info("ServerDaemon::run::Error %s" % e)
            OANServer.shutdown()

    def my_test_connected(self, auth):
        log.info("ServerDaemon::my_test_connected")

    def my_test_closed(self, auth):
        log.info("ServerDaemon::my_test_connected")

    def my_test_message(self, url, messages):
        log.info("ServerDaemon::my_test_messages %s" % len(messages))
        OANServer.push([url], messages)


class TestOanSocket(OANTestCase):
    daemon = None
    daemon2 = None
    auth = None
    start = None

    def setUp(self):
        self.daemon = ServerDaemon(
            "/tmp/ut_socket.pid", stdout='/tmp/ut_socket_out.log',
            stderr='/tmp/ut_socket_err.log')


        self.daemon.auth = OANAuth(
                'oand v1.0', '00000000-0000-code-8000-000000000000',
                'localhost', 8000, False
            )

        self.daemon.start()


        self.daemon2 = ServerDaemon(
            "/tmp/ut_socket_8002.pid", stdout='/tmp/ut_socket_8002_out.log',
            stderr='/tmp/ut_socket_8002_err.log')

        self.daemon2.auth = OANAuth("OAN v0.1", '00000000-0000-code-8002-000000000000', "localhost", 8002, False)

        self.daemon2.start()


        self.reset_all_counters()
        OANCounter.reset()
        self.auth = OANAuth("OAN v0.1", '00000000-0000-code-8001-000000000000', "localhost", 8001, False)
        OANServer.connect_callback = self.my_test_connected
        OANServer.close_callback = self.my_test_closed
        OANServer.error_callback = self.my_test_error
        OANServer.message_callback = self.my_test_message
        OANServer.start(self.auth)

        self.start = time.time()

    def tearDown(self):

        elapsed = (time.time() - self.start)
        (utime, stime, cutime, cstime, elapsed_time) = os.times()
        log.info("Stat: %s, %s, %s, %s, %s sec" % (utime, stime, cutime, cstime, elapsed_time / 10000000000))

        OANServer.shutdown()
        self.daemon.stop()
        self.daemon2.stop()

        if elapsed > 0:
            log.info("sec[%s] avg[%s] in[%s][%s KB] out[%s][%s KB] speed[%s MB/S]" % (
                elapsed, (OANCounter.in_count / elapsed),
                OANCounter.in_count, OANCounter.in_bytes / 1000,
                OANCounter.out_count, OANCounter.out_bytes / 1000,
                OANCounter.out_bytes / elapsed / 1000000)
            )


        log.info(log_counter.result())

    def my_test_connected(self, auth):
        log.info("my_test_connected")
        self.inc_counter('my_test_connected')
        log.info(self.assert_counters)

    def my_test_closed(self, auth):
        self.inc_counter('my_test_closed')
        log.info(self.assert_counters)

    def my_test_message(self, auth, messages):
        self.inc_counter('my_test_message', len(messages))

    def my_test_error(self, url, messages):
        self.inc_counter('my_test_error', len(messages))
        log.info(self.assert_counters)

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

    def atest_push_to_unknown(self):
        """
        Try to push messages to non existing server, all messages should
        be sent to error callback.
        """
        num_push = 100
        to_push = ["M" * 50, "X" * 50, "Y" * 50]

        for x in xrange(0, num_push):
          OANServer.push([("localhost", 8010)], to_push)

        self.assert_counter_wait('my_test_error', num_push * len(to_push))

    def atest_connect(self):
        OANServer.push([("localhost", 8000)], ["M"])
        self.assert_counter_wait('my_test_connected', 1)

    def atest_two_connect(self):
        OANServer.push([("localhost", 8000), ("localhost", 8002)], ["M"])
        self.assert_counter_wait('my_test_connected', 2)

    def test_server(self):
        num_push = 10
        to_push = ["M" * 5, "X" * 5, "Y" * 5]
        urls = [("localhost", 8000), ("localhost", 8002)]

        for x in xrange(0,num_push):
            OANServer.push(urls, to_push)

        self.assert_counter_wait('my_test_message', num_push * len(to_push) * len(urls), timeout=20)


