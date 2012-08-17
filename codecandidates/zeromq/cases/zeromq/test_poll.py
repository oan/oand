import time
import os
import random
import select
from struct import *

from threading import Thread
from Queue import Queue, Empty

from oan.util import log
from test.test_case import OANTestCase


class TestPipeVsQueue(OANTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def create_pipe(self):
        r,w=os.pipe()
        log.info("r:%s,w:%s" % (r,w))
        return r,w

    def write_data(self, fd, str):
        total_count = 0
        num = len(str)
        while total_count < num:
            write_count = os.write(fd, str)

            if write_count > 0:
                total_count += write_count
                str = str[write_count:]
            else:
                log.info("write error")
                return None


    def write_to_queue(self, q, message):
        c = 0
        msg = message
        while True:
            msg = "%s%d" % (message, c)
            size = len(msg)
            q.put(message)
            if (c % 10000 == 0):
                log.info("write: %s %s=%s, %s" % (c, size, bytes, msg))

            c += 1

    def write_to_pipe(self, w, message, counter):
        c = 0
        msg = message
        while c < counter:
            #msg = "%s%d" % (message, c)
            size = len(msg)
            os.write(w, pack('i', size))
            bytes = self.write_data(w, pack('<%ds' % size, msg))
            if (c % 10000 == 0):
                log.info("write: %s %s=%s, %s" % (c, size, bytes, msg))

            c += 1
            #time.sleep(1)

    def read_data(self, fd, num):
        read_count = 0
        data = []
        while read_count < num:
            read_data = os.read(fd, num)
            if read_data:
                read_count += len(read_data)
                data.append(read_data)
            else:
                log.info("read error")
                return None

        return "".join(data)


    def read_from_pipe(self, inputs, counter):
        outputs = []
        c = 0
        while c < counter:
            #readable, writable, exceptional = select.select(inputs, outputs, inputs)
            for fd in inputs:
                (size,)  = unpack('i', self.read_data(fd, 4))
                message = self.read_data(fd, size)
                if (c % 10000 == 0):
                    log.info("read: %s=%s, %s, %s" % (len(message), size, message, c))

                c += 1

    def read_from_queue(self, q):
        c = 0
        while True:
            message = q.get()
            size = len(message)
            if (c % 10000 == 0):
                log.info("read: %s=%s, %s, %s" % (len(message), size, message, c))

            c += 1

    def test_select_pipe(self):

        c = 1000000
        start = time.time()
        inputs = []
        for x in xrange(1,2):
            time.sleep(0.2)
            r, w = self.create_pipe()
            inputs.append(r)
            t = Thread(target=self.write_to_pipe, kwargs={
                'w' : w,
                'message' : "MESSAGE",
                'counter' : c
            })

            t.name="write w%s" % x
            t.start()

        t = Thread(target=self.read_from_pipe, kwargs={
            'inputs' : inputs,
            'counter' : c
         })

        t.name="read_from_pipe"
        t.start()

        t.join()

        elapsed = (time.time() - start)
        (utime, stime, cutime, cstime, elapsed_time) = os.times()

        log.info("sec[%s] avg[%s]" % (
            elapsed, (c / elapsed)
        ))

        log.info("Stat: %s, %s, %s, %s, %s" % (utime, stime, cutime, cstime, elapsed_time))


    def atest_queue(self):

        q = Queue()
        t = Thread(target=self.write_to_queue, kwargs={
            'q' : q,
            'message' : "D" * 1000
        })

        t.name="write_to_queue"
        t.start()

        t = Thread(target=self.read_from_queue, kwargs={
            'q' : q
        })

        t.name="read_from_queue"
        t.start()

        time.sleep(100000)



