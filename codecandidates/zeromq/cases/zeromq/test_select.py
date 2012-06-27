import time
import os
import random
import select
from struct import *

from threading import Thread
from Queue import Queue, Empty

from oan.util import log
from test.test_case import OANTestCase

class TestPoll(OANTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def create_server(self):
        HOST = ''                 # Symbolic name meaning all available interfaces
        PORT = 50007              # Arbitrary non-privileged port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen(5)
        return s.fileno()

    def create_client(self):
        HOST = 'localhost'
        PORT = 50007

        self.connected = False
        self.connecting = True
        err = self.socket.connect_ex(address)
        if err in (EINPROGRESS, EALREADY, EWOULDBLOCK) \
        or err == EINVAL and os.name in ('nt', 'ce'):
            self.addr = address
            return

        if err in (0, EISCONN):
            self.addr = address
            self.handle_connect_event()
        else:
            raise socket.error(err, errorcode[err])

        return s.fileno()


        #conn, addr = s.accept()
        #print 'Connected by', addr
        #while 1:
        #    data = conn.recv(1024)
        #    if not data: break
        #    conn.sendall(data)
        #conn.close()


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


    def write_to_pipe(self, w, message, count = 10):
        c = 0
        msg = message
        for x in xrange(1, count):
            msg = "%s%d" % (message, c)
            size = len(msg)
            os.write(w, pack('i', size))
            bytes = self.write_data(w, pack('<%ds' % size, msg))
            if (c % 10 == 0):
                log.info("write: %s %s=%s, %s" % (c, size, bytes, msg))

            c += 1
            #time.sleep(10)

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


    def read_from_pipe(self, inputs, count = 10):
        outputs = []
        c = 0
        for x in xrange(1, count):
            readable, writable, exceptional = select.select(inputs, outputs, inputs)
            for fd in readable:
                (size,)  = unpack('i', self.read_data(fd, 4))
                message = self.read_data(fd, size)
                if (c % 10 == 0):
                    log.info("read: %s=%s, %s, %s" % (len(message), size, message, c))

                c += 1

    def test_poll_on_pipe(self):

        inputs = []
        for x in xrange(1,100):
            #time.sleep(0.2)
            r, w = self.create_pipe()
            inputs.append(r)
            t = Thread(target=self.write_to_pipe, kwargs={
                'w' : w,
                'message' : "from w%s " % x,
                'count' : 10
            })

            t.name="write w%s" % x
            t.start()


        t = Thread(target=self.read_from_pipe, kwargs={
            'inputs' : inputs,
            'count' : 100
        })

        t.name="read_from_pipe"
        t.start()


