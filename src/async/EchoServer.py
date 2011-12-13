import asyncore
import socket
from Queue import Queue

class EchoBridge(asyncore.dispatcher_with_send):

    out_queue = None
    out_buffer = ''

    in_queue = None
    in_buffer = ''

    def __init__(self, sock, out_queue, in_queue):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.out_queue = out_queue
        self.in_queue = in_queue

    def handle_read(self):
        data = self.recv(8192)
        if data:
            self.in_buffer += data
            pos = self.in_buffer.find('\n')
            if pos > 0:
                self.in_queue.put(self.in_buffer[:pos])
                self.in_buffer = self.in_buffer[pos:]

    def writable(self):
        print "writable:" + str(self.out_queue.empty())
        return not self.out_queue.empty()

    def handle_write(self):
        if (len(self.out_buffer) == 0):
            data = self.out_queue.get(False)
            print data
            if data:
                self.out_buffer = data + '\n'

        sent = self.send(self.out_buffer)
        self.out_buffer = self.out_buffer[sent:]


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
            self.bridges.append(EchoBridge(sock, Queue(), Queue()))
