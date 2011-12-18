
import asyncore, socket
from Queue import Queue


from EchoServer import EchoBridge

class EchoClient(EchoBridge):

    def __init__(self, host, port):
        EchoBridge.__init__(self, None, Queue(), Queue())
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect( (host, port) )
