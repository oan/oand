import sys
import os
import zmq
from  threading import Thread
from Queue import Queue
import time
from collections import deque


class message:
    _data = None

    def __init__ (self, data):
        self._data = data

    def __str__(self):
        return self._data

class fifo:
    def __init__ (self, list=None):
        if not list:
            self.list = deque()
        else:
            self.list = deque(list)

    def __len__ (self):
        return len(self.list)

    def is_empty (self):
        return not self.list

    def first (self):
        return self.list[0]

    def push (self, data):
        self.list.append(data)

    def pop (self):
        if self.list:
            return self.list.popleft()
        else:
            return None

def worker():
    context = zmq.Context()
    work_receiver = context.socket(zmq.PULL)
    work_receiver.connect("tcp://127.0.0.1:5557")

    q = Queue()
    for task_nbr in range(1000000):
        q.put(work_receiver.recv())

    print "got:%s" % q.qsize()

def main():
    context = zmq.Context()
    ventilator_send = context.socket(zmq.PUSH)
    ventilator_send.bind("tcp://127.0.0.1:5557")

    q = fifo()
    r = range(1000000)
    for num in r:
        q.push("MESSAGE")

    for num in r:
        ventilator_send.send(q.pop())

if __name__ == "__main__":
    t = Thread(target=worker, args=())
    t.start()

    start_time = time.time()
    main()
    t.join()

    end_time = time.time()
    duration = end_time - start_time
    msg_per_sec = 1000000 / duration
    (utime, stime, cutime, cstime, elapsed_time) = os.times()

    print "Duration: %s" % duration
    print "Messages Per Second: %s" % msg_per_sec
    print "Stat: %s, %s, %s, %s, %s" % (utime, stime, cutime, cstime, elapsed_time)
