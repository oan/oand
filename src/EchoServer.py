import asyncore
import socket
from Queue import Queue

#import json

#class CommandProxy():
#    def send(self):
#        cmd = {}
#        cmd['name'] = 'add'
#        cmd['param1'] = 1
#        cmd['param2'] = 2
#        return json.dumps(cmd)
#
#    def get(self):
#        args = json.loads(json_args)

import thread
from threading import Thread

class EchoLoop(Thread):
    _running = False

    def __init__(self):
        Thread.__init__(self)

    def start(self):
        if (not self._running):
            self._running = True
            Thread.start(self)

    def stop(self):
        self._running = False

    def run(self):
        print "Loop started"
        while(self._running):
            asyncore.loop(1, False, None, 2)
            print "check _running"

        print "Loop ended"

class EchoBridge(asyncore.dispatcher):

    out_queue = None
    out_buffer = ''

    in_queue = None
    in_buffer = ''

    def __init__(self, sock, out_queue, in_queue):
        asyncore.dispatcher.__init__(self, sock)
        self.out_queue = out_queue
        self.in_queue = in_queue

    def handle_connect(self):
        pass

    def handle_read(self):
        data = self.recv(1024)
        print "handle_read: (%s)" % data

        if data:
            self.in_buffer += data
            pos = self.in_buffer.find('\n')
            print "pos:" + str(pos)
            if pos > -1:
                cmd = self.in_buffer[:pos].strip()
                self.in_queue.put(cmd)
                self.in_buffer = self.in_buffer[pos+1:]
                if (cmd == 'moo'):
                    self.out_queue.put("muu")
                if (cmd == 'close'):
                    self.close()

    def writable(self):
        #print "writable:" + str(not self.out_queue.empty())
        return not self.out_queue.empty()

    def handle_write(self):
        if (len(self.out_buffer) == 0):
            data = self.out_queue.get(False)
            print "handle_write: (%s)" % data
            if data:
                self.out_buffer = data + '\n'

        print "handle_write 2: (%s)" % self.out_buffer
        sent = self.send(self.out_buffer)
        self.out_buffer = self.out_buffer[sent:]

    def handle_close(self):
        print "handle close"
        self.close()

class EchoServer(asyncore.dispatcher):
    bridges = []

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            pass
        else:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(addr)
            self.bridges.append( EchoBridge(sock, Queue(), Queue()) )

    def handle_close(self):
        print "handle close EchoServer"
        self.close()

    #def handle_error(self):
    #    print "handle error"
