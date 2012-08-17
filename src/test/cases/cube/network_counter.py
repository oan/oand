"""
"""
__author__ = "martin@amivono.com, daniel@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin@amivono.com, daniel@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"


class NetworkCounter:
    """
    Statistics for things done by and to a node.

    receive        - received messages
    push           - pushed messages
    send           - sent messages
    disconnect     - disconnects from a remote NetworkView
    connect        - connects to a remote NetworkView
    accept         - accepts of incomming connections
    close          - closed connections.

    """
    receive = None
    push = None
    send = None
    connect = None
    disconnect = None
    accept = None
    close = None

    def __init__(self):
        self.receive = 0
        self.push = 0
        self.send = 0
        self.connect = 0
        self.disconnect = 0
        self.accept = 0
        self.close = 0

    def __str__(self):
        return ("receive:{0:>4}, push:{1:>4}, send:{2:>4}, " +
               "connect:{3:>4}, accept:{4:>4}, "+
               "disconnect:{5:>4}, close:{6:>4}").format(
                    self.receive, self.push, self.send,
                    self.connect, self.accept,
                    self.disconnect, self.close
                )

    def __iadd__(self, obj):
        if isinstance(obj, NetworkCounter):
            self.receive += obj.receive
            self.push += obj.push
            self.send += obj.send
            self.connect += obj.connect
            self.disconnect += obj.disconnect
            self.accept += obj.accept
            self.close += obj.close
            return self
        else:
            raise TypeError("Not a Counter object.")
