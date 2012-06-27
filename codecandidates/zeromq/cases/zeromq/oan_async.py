import select
import socket
import sys
import time
import warnings

import os
from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, EINVAL, \
     ENOTCONN, ESHUTDOWN, EINTR, EISCONN, EBADF, ECONNABORTED, EPIPE, EAGAIN, \
     errorcode

_DISCONNECTED = frozenset((ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED, EPIPE,
                           EBADF))

def _strerror(err):
    try:
        return os.strerror(err)
    except (ValueError, OverflowError, NameError):
        if err in errorcode:
            return errorcode[err]
        return "Unknown error %s" %err


def read(obj):
    try:
        obj.handle_read_event()
    except _reraised_exceptions:
        raise
    except:
        obj.handle_error()

def write(obj):
    try:
        obj.handle_write_event()
    except _reraised_exceptions:
        raise
    except:
        obj.handle_error()

def _exception(obj):
    try:
        obj.handle_expt_event()
    except _reraised_exceptions:
        raise
    except:
        obj.handle_error()

def poll(timeout=0.0, map=None):
    if map is None:
        map = socket_map
    if map:
        r = []; w = []; e = []
        for fd, obj in map.items():
            is_r = obj.readable()
            is_w = obj.writable()
            if is_r:
                r.append(fd)
            # accepting sockets should not be writable
            if is_w and not obj.accepting:
                w.append(fd)
            if is_r or is_w:
                e.append(fd)
        if [] == r == w == e:
            time.sleep(timeout)
            return

        try:
            r, w, e = select.select(r, w, e, timeout)
        except select.error, err:
            if err.args[0] != EINTR:
                raise
            else:
                return

        for fd in r:
            obj = map.get(fd)
            if obj is None:
                continue
            read(obj)

        for fd in w:
            obj = map.get(fd)
            if obj is None:
                continue
            write(obj)

        for fd in e:
            obj = map.get(fd)
            if obj is None:
                continue
            _exception(obj)

def loop(timeout=30.0, use_poll=False, map=None, count=None):
    poll_fun = poll

    if count is None:
        while map:
            poll_fun(timeout, map)

    else:
        while map and count > 0:
            poll_fun(timeout, map)
            count = count - 1

class OANBridge:
    addr

class OANAsync:
    sockets = {}

    @staticmethod
    def add_socket(sock):
        if sock:
            # Set to nonblocking just to make sure for cases where we
            # get a socket from a blocking source.
            sock.setblocking(0)
            OANAsync.set_socket(sock, map)

            # The constructor no longer requires that the socket
            # passed be connected.
            try:
                self.addr = sock.getpeername()
            except socket.error, err:
                if err.args[0] in (ENOTCONN, EINVAL):
                    # To handle the case where we got an unconnected
                    # socket.
                    self.connected = False
                else:
                    # The socket is broken in some unknown way, alert
                    # the user and remove it from the map (to prevent
                    # polling of broken sockets).
                    self.del_channel(map)
                    raise
        else:
            self.socket = None

    def __repr__(self):
        status = [self.__class__.__module__+"."+self.__class__.__name__]
        if self.accepting and self.addr:
            status.append('listening')
        elif self.connected:
            status.append('connected')
        if self.addr is not None:
            try:
                status.append('%s:%d' % self.addr)
            except TypeError:
                status.append(repr(self.addr))
        return '<%s at %#x>' % (' '.join(status), id(self))

    __str__ = __repr__

    def add_channel(self, map=None):
        #self.log_info('adding channel %s' % self)
        if map is None:
            map = self._map
        map[self._fileno] = self

    def del_channel(self, map=None):
        fd = self._fileno
        if map is None:
            map = self._map
        if fd in map:
            #self.log_info('closing channel %d:%s' % (fd, self))
            del map[fd]
        self._fileno = None

    def create_socket(self, family, type):
        self.family_and_type = family, type
        sock = socket.socket(family, type)
        sock.setblocking(0)
        self.set_socket(sock)

    def set_socket(self, sock, map=None):
        self.socket = sock
##        self.__dict__['socket'] = sock
        self._fileno = sock.fileno()
        self.add_channel(map)

    def set_reuse_addr(self):
        # try to re-use a server port if possible
        try:
            self.socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR,
                self.socket.getsockopt(socket.SOL_SOCKET,
                                       socket.SO_REUSEADDR) | 1
                )
        except socket.error:
            pass

    # ==================================================
    # socket object methods.
    # ==================================================

    def listen(self, num):
        self.accepting = True
        if os.name == 'nt' and num > 5:
            num = 5
        return self.socket.listen(num)

    def bind(self, addr):
        self.addr = addr
        return self.socket.bind(addr)

    def connect(self, address):
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

    def accept(self):
        # XXX can return either an address pair or None
        try:
            conn, addr = self.socket.accept()
        except TypeError:
            return None
        except socket.error as why:
            if why.args[0] in (EWOULDBLOCK, ECONNABORTED, EAGAIN):
                return None
            else:
                raise
        else:
            return conn, addr

    def send(self, data):
        try:
            result = self.socket.send(data)
            return result
        except socket.error, why:
            if why.args[0] == EWOULDBLOCK:
                return 0
            elif why.args[0] in _DISCONNECTED:
                self.handle_close()
                return 0
            else:
                raise

    def recv(self, buffer_size):
        try:
            data = self.socket.recv(buffer_size)
            if not data:
                # a closed connection is indicated by signaling
                # a read condition, and having recv() return 0.
                self.handle_close()
                return ''
            else:
                return data
        except socket.error, why:
            # winsock sometimes throws ENOTCONN
            if why.args[0] in _DISCONNECTED:
                self.handle_close()
                return ''
            else:
                raise

    def close(self):
        self.connected = False
        self.accepting = False
        self.connecting = False
        self.del_channel()
        try:
            self.socket.close()
        except socket.error, why:
            if why.args[0] not in (ENOTCONN, EBADF):
                raise

    # cheap inheritance, used to pass all other attribute
    # references to the underlying socket object.
    def __getattr__(self, attr):
        try:
            retattr = getattr(self.socket, attr)
        except AttributeError:
            raise AttributeError("%s instance has no attribute '%s'"
                                 %(self.__class__.__name__, attr))
        else:
            msg = "%(me)s.%(attr)s is deprecated. Use %(me)s.socket.%(attr)s " \
                  "instead." % {'me': self.__class__.__name__, 'attr':attr}
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return retattr

    # log and log_info may be overridden to provide more sophisticated
    # logging and warning methods. In general, log is for 'hit' logging
    # and 'log_info' is for informational, warning and error logging.

    def log(self, message):
        sys.stderr.write('log: %s\n' % str(message))

    def log_info(self, message, type='info'):
        if type not in self.ignore_log_types:
            print '%s: %s' % (type, message)

    def handle_read_event(self):
        if self.accepting:
            # accepting sockets are never connected, they "spawn" new
            # sockets that are connected
            self.handle_accept()
        elif not self.connected:
            if self.connecting:
                self.handle_connect_event()
            self.handle_read()
        else:
            self.handle_read()

    def handle_connect_event(self):
        err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if err != 0:
            raise socket.error(err, _strerror(err))
        self.handle_connect()
        self.connected = True
        self.connecting = False

    def handle_write_event(self):
        if self.accepting:
            # Accepting sockets shouldn't get a write event.
            # We will pretend it didn't happen.
            return

        if not self.connected:
            if self.connecting:
                self.handle_connect_event()

        self.handle_write()

    def handle_expt_event(self):
        # handle_expt_event() is called if there might be an error on the
        # socket, or if there is OOB data
        # check for the error condition first
        err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if err != 0:
            # we can get here when select.select() says that there is an
            # exceptional condition on the socket
            # since there is an error, we'll go ahead and close the socket
            # like we would in a subclassed handle_read() that received no
            # data
            self.handle_close()
        else:
            self.handle_expt()

    def handle_error(self):
        nil, t, v, tbinfo = compact_traceback()

        # sometimes a user repr method will crash.
        try:
            self_repr = repr(self)
        except:
            self_repr = '<__repr__(self) failed for object at %0x>' % id(self)

        self.log_info(
            'uncaptured python exception, closing channel %s (%s:%s %s)' % (
                self_repr,
                t,
                v,
                tbinfo
                ),
            'error'
            )
        self.handle_close()

    def handle_expt(self):
        self.log_info('unhandled incoming priority event', 'warning')

    def handle_read(self):
        self.log_info('unhandled read event', 'warning')

    def handle_write(self):
        self.log_info('unhandled write event', 'warning')

    def handle_connect(self):
        self.log_info('unhandled connect event', 'warning')

    def handle_accept(self):
        self.log_info('unhandled accept event', 'warning')

    def handle_close(self):
        self.log_info('unhandled close event', 'warning')
        self.close()
