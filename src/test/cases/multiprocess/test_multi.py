
import multiprocessing

from threading import Thread
from multiprocessing.managers import BaseManager, SyncManager
from oan.util import log
from test.test_case import OANTestCase

#
# This module shows how to use arbitrary callables with a subclass of
# `BaseManager`.
#
# Copyright (c) 2006-2008, R Oudkerk
# All rights reserved.
#

from time import sleep
from multiprocessing import Manager, freeze_support
from multiprocessing.managers import BaseManager, BaseProxy
import operator

##

class NodeList(object):
    _running = None
    _oan_id = None
    _node_dict = None

    def start(self, oan_id, node_dict):
        self._running = True
        self._oan_id = oan_id
        self._node_dict = node_dict

        t = Thread(target=self.generate, kwargs={})
        t.name="node_list %s " % self._oan_id
        t.start()

    def generate(self):
        c = 0
        while self._running:
            self._node_dict[c] = self._oan_id
            #log.info(self._node_dict)
            sleep(0.01)
            c += 1

    def stop(self):
        self._running = False


class Foo(object):
    def f(self):
        print 'you called Foo.f()'
    def g(self):
        print 'you called Foo.g()'
    def _h(self):
        print 'you called Foo._h()'

# A simple generator function
def baz():
    for i in xrange(10000):
        log.info("asdfsdf")
        yield i

# Proxy type for generator objects
class GeneratorProxy(BaseProxy):
    _exposed_ = ('next', '__next__')
    def __iter__(self):
        return self
    def next(self):
        return self._callmethod('next')
    def __next__(self):
        return self._callmethod('__next__')

# Function to return the operator module
def get_operator_module():
    return operator

##

class MyManager(SyncManager):
    def __init__(self):
        BaseManager.__init__(self, address=('', 50000))

# register the Foo class; make `g()` and `_h()` accessible via proxy
MyManager.register('NodeList1', NodeList)

# register the Foo class; make `f()` and `g()` accessible via proxy
MyManager.register('Foo1', Foo)

# register the Foo class; make `g()` and `_h()` accessible via proxy
MyManager.register('Foo2', Foo, exposed=('g', '_h'))

# register the generator function baz; use `GeneratorProxy` to make proxies
MyManager.register('baz', baz, proxytype=GeneratorProxy)

# register get_operator_module(); make public functions accessible via proxy
MyManager.register('operator', get_operator_module)

class TestMulti(OANTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_multi(self):
        #freeze_support()

        server = MyManager()
        server.start()
        #server = server_manager.get_server()
        #t = Thread(target=server.serve_forever, kwargs={})
        #t.name="serv"
        #t.start()

        manager = MyManager()
        manager.connect()

        node_dict = manager.dict()
        nodeList = manager.NodeList1()
        nodeList.start("id1", node_dict)

        log.info('-' * 20)

        f1 = manager.Foo1()
        f1.f()
        f1.g()
        assert not hasattr(f1, '_h')
        assert sorted(f1._exposed_) == sorted(['f', 'g'])

        log.info('-' * 20)

        f2 = manager.Foo2()
        f2.g()
        f2._h()
        assert not hasattr(f2, 'f')
        assert sorted(f2._exposed_) == sorted(['g', '_h'])

        log.info('-' * 20)

        it = manager.baz()
        for i in it:
            log.info('<%d>' % i),
            if i > 10: break

        log.info('-' * 20)

        op = manager.operator()
        log.info('op.add(23, 45) = %s' % op.add(23, 45))
        log.info('op.pow(2, 94) = %s' % op.pow(2, 94))
        log.info('op.getslice(range(10), 2, 6) = %s' % op.getslice(range(10), 2, 6))
        log.info('op.repeat(range(5), 3) = %s' % op.repeat(range(5), 3))
        log.info('op._exposed_ = %s' % str(op._exposed_))

        while True:
            log.info(node_dict)
            sleep(10)

        server.shutdown()
