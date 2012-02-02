#
# Simple benchmarks for the multiprocessing package
#
# Copyright (c) 2006-2008, R Oudkerk
# All rights reserved.
#

import time, sys, multiprocessing, threading, Queue, gc

if sys.platform == 'win32':
    _timer = time.clock
else:
    _timer = time.time

delta = 1


#### TEST_QUEUESPEED

def queuespeed_func(q, c, iterations):
    a = '0' * 256
    c.acquire()
    c.notify()
    c.release()

    for i in xrange(iterations):
        q.put(a)

    q.put('STOP')

def test_queuespeed(Process, q, c):
    elapsed = 0
    iterations = 1

    while elapsed < delta:
        iterations *= 2

        p = Process(target=queuespeed_func, args=(q, c, iterations))
        c.acquire()
        p.start()
        c.wait()
        c.release()

        result = None
        t = _timer()

        while result != 'STOP':
            result = q.get()

        elapsed = _timer() - t

        p.join()

    print iterations, 'objects passed through the queue in', elapsed, 'seconds'
    print 'average number/sec:', iterations/elapsed


#### TEST_PIPESPEED

def pipe_func(c, cond, iterations):
    a = '0' * 256
    cond.acquire()
    cond.notify()
    cond.release()

    for i in xrange(iterations):
        c.send(a)

    c.send('STOP')

def test_pipespeed():
    c, d = multiprocessing.Pipe()
    cond = multiprocessing.Condition()
    elapsed = 0
    iterations = 1

    while elapsed < delta:
        iterations *= 2

        p = multiprocessing.Process(target=pipe_func,
                                    args=(d, cond, iterations))
        cond.acquire()
        p.start()
        cond.wait()
        cond.release()

        result = None
        t = _timer()

        while result != 'STOP':
            result = c.recv()

        elapsed = _timer() - t
        p.join()

    print iterations, 'objects passed through connection in',elapsed,'seconds'
    print 'average number/sec:', iterations/elapsed


#### TEST_SEQSPEED

def test_seqspeed(seq):
    elapsed = 0
    iterations = 1

    while elapsed < delta:
        iterations *= 2

        t = _timer()

        for i in xrange(iterations):
            a = seq[5]

        elapsed = _timer()-t

    print iterations, 'iterations in', elapsed, 'seconds'
    print 'average number/sec:', iterations/elapsed


#### TEST_LOCK

def test_lockspeed(l):
    elapsed = 0
    iterations = 1

    while elapsed < delta:
        iterations *= 2

        t = _timer()

        for i in xrange(iterations):
            l.acquire()
            l.release()

        elapsed = _timer()-t

    print iterations, 'iterations in', elapsed, 'seconds'
    print 'average number/sec:', iterations/elapsed


#### TEST_CONDITION

def conditionspeed_func(c, N):
    c.acquire()
    c.notify()

    for i in xrange(N):
        c.wait()
        c.notify()

    c.release()

def test_conditionspeed(Process, c):
    elapsed = 0
    iterations = 1

    while elapsed < delta:
        iterations *= 2

        c.acquire()
        p = Process(target=conditionspeed_func, args=(c, iterations))
        p.start()

        c.wait()

        t = _timer()

        for i in xrange(iterations):
            c.notify()
            c.wait()

        elapsed = _timer()-t

        c.release()
        p.join()

    print iterations * 2, 'waits in', elapsed, 'seconds'
    print 'average number/sec:', iterations * 2 / elapsed

####

def test():
    manager = multiprocessing.Manager()

    gc.disable()

    print '\n\t######## testing Queue.Queue\n'
    test_queuespeed(threading.Thread, Queue.Queue(),
                    threading.Condition())
    print '\n\t######## testing multiprocessing.Queue\n'
    test_queuespeed(multiprocessing.Process, multiprocessing.Queue(),
                    multiprocessing.Condition())
    print '\n\t######## testing Queue managed by server process\n'
    test_queuespeed(multiprocessing.Process, manager.Queue(),
                    manager.Condition())
    print '\n\t######## testing multiprocessing.Pipe\n'
    test_pipespeed()

    print

    print '\n\t######## testing list\n'
    test_seqspeed(range(10))
    print '\n\t######## testing list managed by server process\n'
    test_seqspeed(manager.list(range(10)))
    print '\n\t######## testing Array("i", ..., lock=False)\n'
    test_seqspeed(multiprocessing.Array('i', range(10), lock=False))
    print '\n\t######## testing Array("i", ..., lock=True)\n'
    test_seqspeed(multiprocessing.Array('i', range(10), lock=True))

    print

    print '\n\t######## testing threading.Lock\n'
    test_lockspeed(threading.Lock())
    print '\n\t######## testing threading.RLock\n'
    test_lockspeed(threading.RLock())
    print '\n\t######## testing multiprocessing.Lock\n'
    test_lockspeed(multiprocessing.Lock())
    print '\n\t######## testing multiprocessing.RLock\n'
    test_lockspeed(multiprocessing.RLock())
    print '\n\t######## testing lock managed by server process\n'
    test_lockspeed(manager.Lock())
    print '\n\t######## testing rlock managed by server process\n'
    test_lockspeed(manager.RLock())

    print

    print '\n\t######## testing threading.Condition\n'
    test_conditionspeed(threading.Thread, threading.Condition())
    print '\n\t######## testing multiprocessing.Condition\n'
    test_conditionspeed(multiprocessing.Process, multiprocessing.Condition())
    print '\n\t######## testing condition managed by a server process\n'
    test_conditionspeed(multiprocessing.Process, manager.Condition())

    gc.enable()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    test()



fo-tp-dali-4:codecandidates dali$ python thread_vs_process.py

    ######## testing Queue.Queue

65536 objects passed through the queue in 1.6856238842 seconds
average number/sec: 38879.3731593

    ######## testing multiprocessing.Queue

16384 objects passed through the queue in 1.15573215485 seconds
average number/sec: 14176.2950276

    ######## testing Queue managed by server process

4096 objects passed through the queue in 1.01277899742 seconds
average number/sec: 4044.31767486

    ######## testing multiprocessing.Pipe

32768 objects passed through connection in 1.31182408333 seconds
average number/sec: 24978.9590056


    ######## testing list

4194304 iterations in 1.06850600243 seconds
average number/sec: 3925391.14472

    ######## testing list managed by server process

8192 iterations in 1.31103897095 seconds
average number/sec: 6248.47939805

    ######## testing Array("i", ..., lock=False)

4194304 iterations in 2.16587710381 seconds
average number/sec: 1936538.31634

    ######## testing Array("i", ..., lock=True)

131072 iterations in 1.53971195221 seconds
average number/sec: 85127.6109222


    ######## testing threading.Lock

524288 iterations in 1.55534791946 seconds
average number/sec: 337087.280241

    ######## testing threading.RLock

65536 iterations in 1.0125541687 seconds
average number/sec: 64723.4508787

    ######## testing multiprocessing.Lock

131072 iterations in 1.17517900467 seconds
average number/sec: 111533.646771

    ######## testing multiprocessing.RLock

262144 iterations in 1.89785599709 seconds
average number/sec: 138126.391255

    ######## testing lock managed by server process

4096 iterations in 1.4197769165 seconds
average number/sec: 2884.96027255

    ######## testing rlock managed by server process

4096 iterations in 1.40835285187 seconds
average number/sec: 2908.36205896


    ######## testing threading.Condition

16384 waits in 1.38426804543 seconds
average number/sec: 11835.8579858

    ######## testing multiprocessing.Condition

16384 waits in 1.66948509216 seconds
average number/sec: 9813.80431422

    ######## testing condition managed by a server process

2048 waits in 1.6663248539 seconds
average number/sec: 1229.05206341
fo-tp-dali-4:codecandidates dali$
