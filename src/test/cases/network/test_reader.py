import time
import os
import random
import select
import socket

from struct import *

from oan.util.queue import OANQueue
from oan.util import log
from oan.network.server import OANReader, OANNetworkError, OANCounter, OANLogCounter
from test.test_case import OANTestCase

class FakeSocket():
    _frame_size = None
    _frame_count = None
    _message_size = None
    _block_size = None
    _data = None
    _data_size = 0
    _pos = 0
    _fd = None
    _handshake = None

    def __init__(self, fd, handshake, frame_size, frame_count, message_size, block_size):
        self._fd = fd
        self._handshake = handshake
        self._frame_size = frame_size
        self._frame_count = frame_count
        self._message_size = message_size
        self._block_size = block_size
        self._data_size = 0
        self._generate_data()

    def fileno(self):
        return self._fd

    def recv(self, bufsize):
        if self._pos < self._data_size:
            size = min(self._block_size, bufsize)

            if self._pos + size < self._data_size:
                ret = self._data[self._pos:self._pos + size]
            else:
                ret = self._data[self._pos:]

            self._pos += len(ret)
            return ret

        return  None

    def _generate_data(self):

        tmp = []
        for c in xrange(0, self._frame_count):

            if self._handshake:
                buf = [self._handshake]
                self._handshake = None
            else:
                buf = []

            buf.extend(['D'* self._message_size] * (self._frame_size / self._message_size))
            if self._frame_size % self._message_size != 0:
                buf.append('D' * (self._frame_size % self._message_size))

            data = '\n'.join(buf)
            tmp.append(pack('i', len(data)))
            tmp.append(data)

        self._data = ''.join(tmp)
        self._data_size = len(self._data)
        log.info("_generate_data size : %s" % self._data_size)

class TestOanReader(OANTestCase):
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


        log.info(OANLogCounter.result())


    def do_fake_socket_test(self, frame_size, frame_count, message_size, block_size, buf_size):
        sock = FakeSocket(1, "", frame_size, frame_count, message_size, block_size)

        total = []

        while True:
            data = sock.recv(buf_size)
            if data:
                total.append(data)
            else:
                break

        buf = ''.join(total)
        (size,)  = unpack('i', buf[0:4])
        lines = buf[4:size].split('\n')
        return lines

    def test_fake_socket(self):
        self.assertEqual(self.do_fake_socket_test(
                         frame_size = 20, frame_count = 1, message_size = 20,
                         block_size = 3, buf_size = 4096),
                         ['DDDDDDDDDDDDDDDD'])

        self.assertEqual(self.do_fake_socket_test(
                         frame_size = 10, frame_count = 1,  message_size = 2,
                         block_size = 30, buf_size = 4096),
                         ['DD', 'DD', 'DD', 'D'])

        self.assertEqual(self.do_fake_socket_test(
                         frame_size = 30, frame_count = 1,  message_size = 5,
                         block_size = 10, buf_size = 4096),
                         ['DDDDD', 'DDDDD', 'DDDDD', 'DDDDD', 'DDDDD', 'D'])

        self.assertEqual(self.do_fake_socket_test(
                         frame_size = 30, frame_count = 1, message_size = 20,
                         block_size = 10, buf_size = 2),
                         ['DDDDDDDDDDDDDDDDDDDD', 'DDDDDD'])

        self.assertEqual(self.do_fake_socket_test(
                         frame_size = 40, frame_count = 1,  message_size = 20,
                         block_size = 30, buf_size = 2),
                         ['DDDDDDDDDDDDDDDDDDDD', 'DDDDDDDDDDDDDDDD'])

    all_messages = None
    def message_cb(self, fd, sock, auth, messages):
        self.all_messages.extend(messages)

    def connect_cb(self, fd, sock, auth):
        log.info("connect_cb")

    def close_cb(self, fd, sock, auth):
        log.info("close_cb")

    def test_handle_read(self):
        frame_size = 100
        frame_count = 1000
        message_size = 100
        block_size = 10

        reader = OANReader(FakeSocket(1, handshake = "OAN %s %s %s" % (
                                                        "0000-8000",
                                                        "localhost",
                                                        8000),
                                         frame_size = frame_size,
                                         frame_count = frame_count,
                                         message_size = message_size,
                                         block_size = block_size),
                           message_callback = self.message_cb,
                           connect_callback = self.connect_cb,
                           close_callback = self.close_cb

        )

        self.all_messages = []
        try:
            while True:
                reader.handle()
        except OANNetworkError, e:
            log.info(e)

        self.assertEqual(len(''.join(self.all_messages)), frame_size * frame_count)
