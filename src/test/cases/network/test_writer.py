import time
import os

from struct import *

from oan.network.server import OANWriter, OANCounter
from oan.util import log
from oan.util import log_counter

from test.test_case import OANTestCase

class FakeSocket():
    _block_size = None
    _fd = None
    _buffer = None

    def __init__(self, fd, block_size):
        self._fd = fd
        self._block_size = block_size
        self._buffer = []

    def fileno(self):
        return self._fd

    def send(self, data):
        size = min(self._block_size, len(data))
        self._buffer.append(data[:size])
        return size

    def get_value(self):
        return ''.join(self._buffer)

class TestOanWriter(OANTestCase):
    start = None

    def setUp(self):
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


        log.info(log_counter.result())


    def do_fake_socket_test(self, message_size, block_size, buf_size):
        sock = FakeSocket(1, block_size)

        data = 'D' * message_size
        pos = 0
        while pos < message_size:
            sent = sock.send(data[pos:pos + buf_size])
            pos += sent

        return sock.get_value()

    def test_fake_socket(self):
        self.assertEqual(self.do_fake_socket_test(
                         message_size = 20,
                         block_size = 3, buf_size = 4096),
                         'DDDDDDDDDDDDDDDDDDDD')

        self.assertEqual(self.do_fake_socket_test(
                         message_size = 2,
                         block_size = 30, buf_size = 4096),
                         'DD')

        self.assertEqual(self.do_fake_socket_test(
                         message_size = 50,
                         block_size = 10, buf_size = 4096),
                         'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD')

        self.assertEqual(self.do_fake_socket_test(
                         message_size = 20,
                         block_size = 10, buf_size = 2),
                         'DDDDDDDDDDDDDDDDDDDD')

        self.assertEqual(self.do_fake_socket_test(
                         message_size = 20,
                         block_size = 30, buf_size = 2),
                         'DDDDDDDDDDDDDDDDDDDD')

    def test_handle_write(self):

        sock = FakeSocket(1, block_size = 10)
        writer = OANWriter(sock)

        messages = ['D' * 1000] * 10
        writer.push(messages)

        while not writer.empty():
            writer.handle()

        buf = sock.get_value()
        (size,)  = unpack('i', buf[:4])
        lines = buf[4:].split('\n')

        self.assertEqual(lines, messages)


