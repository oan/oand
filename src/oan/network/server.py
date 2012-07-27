import time
import select
import socket
from struct import *
from collections import deque

from threading import Thread, Lock, Event, Condition
from oan.util import log

class OANNetworkError(Exception): pass

class OANCounter:
    out_bytes = 0
    out_count = 0
    out_writes = 0
    in_bytes = 0
    in_count = 0
    in_reads = 0

class OANMessageDictionary:
    _messages = None
    _lock = None
    _cond = None
    _is_waiting = None

    def __init__(self):
        self._messages = {}
        self._is_waiting = False
        self._lock = Lock()
        self._cond = Condition(self._lock)

    def push(self, urls, messages):
        with self._lock:
            for url in urls:
                if url in self._messages:
                    self._messages[url].extend(messages)
                else:
                    self._messages[url] = messages[:]

            if self._is_waiting:
                self._cond.notify()

    def interrupt(self):
        with self._lock:
            if self._is_waiting:
                self._cond.notify()

    def clear(self, urls):
        with self._lock:
            for url in urls:
                if url in self._messages:
                    del self._messages[url]

    def pop(self, urls, exclude, block = True):
        """
        if url is in urls, it will always get a entry back.
        if url is, in exclude

        """
        with self._lock:

            keys = []
            for key in self._messages.keys():
                if key in urls or key not in exclude:
                    keys.append(key)

            if not keys and block:
                self._is_waiting = True
                self._cond.wait()
                self._is_waiting = False

            ret = []
            for url in keys:
                if url in urls:
                    ret.append((url, True, self._messages[url]))
                    del self._messages[url]
                else:
                    ret.append((url, False, self._messages[url]))

            return ret

class OANSendNotify:
    auth = None
    _socket = None

    def __init__(self, socket):
        self.auth = None
        self._socket = socket

    def close(self):
        self._socket.close()

    def handle(self):
        self._socket.send('\n')
        #log.info("OANSendNotify")

class OANRecvNotify:
    auth = None
    _socket = None

    def __init__(self, socket):
        self.auth = None
        self._socket = socket

    def close(self):
        self._socket.close()

    def handle(self):
        self._socket.recv(256)
        #log.info("OANRecvNotify")

class OANLogEntry():
    counter = None
    last_elapsed = None
    total_elapsed = None
    min_elapsed = None
    max_elapsed = None

    def __init__(self):
        self.counter = 0
        self.last_elapsed = 0
        self.total_elapsed = 0
        self.min_elapsed = None
        self.max_elapsed = 0

    def __str__(self):
        return ("counter:{0:>6}, total:{1:>20}, avg:{2:>20}, " +
                       "min:{3:>20}, max:{4:>20}").format(
                            self.counter, self.total_elapsed,
                            self.total_elapsed / (self.counter or 1),
                            self.min_elapsed, self.max_elapsed
                        )

class OANLogCounter():

    _entries = {}

    @staticmethod
    def begin(key):
        if key not in OANLogCounter._entries:
            entry = OANLogEntry()
            OANLogCounter._entries[key] = entry
        else:
            entry = OANLogCounter._entries[key]

        entry.start = time.time()

    @staticmethod
    def end(key):
        entry = OANLogCounter._entries[key]
        entry.counter += 1
        entry.last_elapsed = (time.time() - entry.start)
        entry.total_elapsed += entry.last_elapsed
        entry.max_elapsed = max(entry.last_elapsed, entry.max_elapsed)
        if entry.min_elapsed == None:
           entry.min_elapsed = entry.last_elapsed
        else:
            entry.min_elapsed = min(entry.last_elapsed, entry.min_elapsed)

    @staticmethod
    def result():

        ret = ""
        for key, entry in OANLogCounter._entries.items():
            ret += "\n{0:<15} -> {1}".format(key, str(entry))

        return ret


class OANListen:
    _socket = None
    _accept_callback = None

    def __init__(self, socket, accept_callback = lambda sock : None):
        self._socket = socket
        self._accept_callback = accept_callback

    def close(self):
        self._socket.close()

    def handle(self):
        sock, addr = self._socket.accept()
        sock.setblocking(0)
        self._accept_callback(sock)
        #log.info("OANListen")


class OANReader:

    auth = None
    _socket = None
    _fd = None
    _message_callback = None
    _connect_callback = None
    _close_callback = None
    _buffer = None
    _buffer_size = None
    _frame_size = None
    _connected = None

    def __init__(self, socket,
                 message_callback = lambda fd, sock, auth, messages : None,
                 connect_callback = lambda fd, sock, auth : None,
                 close_callback = lambda fd, sock, auth : None
                ):
        self._socket = socket
        self._fd = socket.fileno()
        self._message_callback = message_callback
        self._connect_callback = connect_callback
        self._close_callback = close_callback
        self._buffer = deque()
        self._buffer_size = 0
        self._frame_size = 0
        self._connected = False

    def fileno(self):
        return self._fd

    def close(self):
        self._socket.close()
        self._close_callback(self._fd, self._socket, self.auth)

    def handle(self):
        """
        method called by OANIn when it's time to read from the socket.
        """
        OANLogCounter.begin("handle_read")
        self._read_data()

        ret = []
        while True:

            if self._frame_size == 0:
                data = self._get_data(4)
                if data:
                    (self._frame_size,)  = unpack('i', data)
                else:
                    break

            if self._frame_size > 0:
                data = self._get_data(self._frame_size)
                if data:
                    self._frame_size = 0
                    ret.extend(data.splitlines())
                else:
                    break

        OANLogCounter.end("handle_read")
        if ret:
            OANCounter.in_count += len(ret)
            if not self._connected:
                self._connected = True
                self._connect_callback(self._fd, self._socket, self._create_auth(ret[0]))
                del ret[0]

            if ret:
                self._message_callback(self._fd, self._socket, self.auth, ret)

    def _create_auth(self, handshake):
        #log.info("_create_auth %s" % handshake)

        try:
            protocol, oan_id, host, port = handshake.split(' ')
            return OANAuth(protocol, oan_id, host, int(port), False)
        except Exception, e:
            raise e

    def _read_data(self):
        """
        Reads data from the socket and push it to the buffer
        and increase _buffer_size.
        """
        data = self._socket.recv(100000)
        if data:
            OANCounter.in_reads += 1
            OANCounter.in_bytes += len(data)
            self._buffer_size += len(data)
            self._buffer.append(data)
        else:
            raise OANNetworkError("socket closed")

    def _get_data(self, bytes):
        """
        Get number of bytes from the buffer, if buffer not contains enough just
        return None. pop data from the buffer and decrease _buffer_size.
        """
        if self._buffer_size >= bytes:
            OANLogCounter.begin("_get_data")
            tmp = []
            size = 0
            while size < bytes:
                msg = self._buffer.popleft()
                if size + len(msg) > bytes:
                    s = bytes-size
                    tmp.append(msg[:s])
                    self._buffer.appendleft(msg[s:])
                else:
                    s = len(msg)
                    tmp.append(msg)

                size += s
                self._buffer_size -= s

            OANLogCounter.end("_get_data")
            return ''.join(tmp)

        return None


class OANWriter:
    auth = None

    _socket = None
    _connect_callback = None
    _close_callback = None
    _fd = None
    _buffer = None
    _data = None
    _connected = None
    _current = None
    _size = None

    def __init__(self, socket,
            connect_callback = lambda fd, sock: None,
            close_callback = lambda fd, sock, auth : None):
        self._connected = False
        self._socket = socket
        self._fd = socket.fileno()
        self._connect_callback = connect_callback
        self._close_callback = close_callback
        self._buffer = []
        self._current = 0
        self._size = 0
        self._data = ""

    def fileno(self):
        return self._fd

    def close(self):
        self._socket.close()
        self._close_callback(self._fd, self._socket, self.auth)

    def handshake(self, auth):
        self.push([self._create_handshake(auth)])

    def push(self, messages):
        for message in messages:
            self._buffer.append(message)
            self._size += len(message)

        #log.info(self._buffer)

    def empty(self):
        return len(self._buffer) == 0 and len(self._data) == self._current

    def handle(self):

        OANLogCounter.begin("handle_write")

        # fill buffer
        if len(self._buffer) > 0 and len(self._data) == self._current:
            self._data = self._pack(self._buffer)
            self._current = 0
            self._size = 0
            self._buffer = []

        ## send data
        if self._data:
            if not self._connected:
                self._connected = True
                self._send_all()
                self._connect_callback(self._fd, self._socket)
            else:
                self._send()

        OANLogCounter.end("handle_write")


    def _pack(self, buffer):
        tmp = []
        tmp.append(pack('i', self._size + (len(self._buffer)-1)))
        tmp.append('\n'.join(self._buffer))
        OANCounter.out_count += len(self._buffer)
        return ''.join(tmp)


    def _send_all(self):
        while not self.empty():
            self._send()

    def _send(self):
        sent = self._socket.send(self._data[self._current:self._current + 64000])
        self._current += sent
        OANCounter.out_bytes += sent
        OANCounter.out_writes += 1

    def _create_handshake(self, auth):
        handshake = "OAN %s %s %s" % (
            OANServer.auth.oan_id,
            OANServer.auth.host,
            OANServer.auth.port)

        return handshake


class OANOut:

    _out = OANMessageDictionary()
    _writers = {}
    _authorized = {}
    _connecting = {}
    _fds = []
    _thread = None
    _started = None
    _send_notify = None

    connect_callback = staticmethod(lambda fd, sock : None)
    close_callback = staticmethod(lambda fd, sock : None)
    accept_callback = staticmethod(lambda fd, sock : None)
    error_callback = staticmethod(lambda url, messages : None)

    @staticmethod
    def start(notify_sock):
        OANOut._send_notify = OANSendNotify(notify_sock)
        OANOut._writers[notify_sock.fileno()] = OANOut._send_notify

        OANOut._started = Event()
        OANOut._thread = Thread(target=OANOut._run, kwargs={})
        OANOut._thread.name="out"
        OANOut._thread.start()
        OANOut._started.wait()

    @staticmethod
    def shutdown():
        log.info("OANOut: shutdown begin")
        OANOut._out.interrupt()
        OANOut._thread.join()

    @staticmethod
    def push(urls, messages):
        OANOut._out.push(urls, messages)

    @staticmethod
    def authorized(fd, auth):
        #todo handle missing writers
        OANOut._writers[fd].auth = auth
        OANOut._authorized[auth.url] = OANOut._writers[fd]
        OANOut._out.interrupt()

    @staticmethod
    def handshake(sock, auth):
        writer = OANWriter(sock, OANOut._connect_occured, OANOut._close_occured)
        writer.handshake(auth)
        OANOut._writers[writer.fileno()] = writer
        OANOut._fds.append(writer.fileno())
        OANOut._out.interrupt()

    @staticmethod
    def _connect_occured(fd, sock):
        try:
            #log.info("OANOut:_connect_occured %s" % fd)
            OANOut.connect_callback(fd, sock)
        except Exception, e:
            log.info("_connect_occured %s %s" % (fd, e))

        OANOut._send_notify.handle()

    @staticmethod
    def _close_occured(fd, sock, auth):
        try:
            #log.info("OANOut:_close_occured %s" % fd)
            OANOut.close_callback(fd, sock)
        except Exception, e:
            log.info("_disconnect_occured %s %s" % (fd, e))

    @staticmethod
    def _accept_occured(sock):
        #log.info("OANIn: accept %s " % sock.fileno())
        OANIn.accept_callback(sock)

    @staticmethod
    def _connect(url):
        #todo: add errors from asyncore.
        if url not in OANOut._connecting:
            log.info("OANOut:_connect (%s, %s)" % url)

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setblocking(0)
            err = s.connect_ex(url)

            err = s.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            if err != 0:
                log.info("my socket err %s" % err)

            OANOut._connecting[url] = s.fileno()
            OANOut._accept_occured(s)

    @staticmethod
    def _close_all():
        for fd in OANOut._writers.keys()[:]:
            OANOut._close(fd)

    @staticmethod
    def _close(fd):
        log.info("OANOut: _close %s, %s" % (fd, OANOut._connecting))
        if fd in OANOut._writers:
            writer = OANOut._writers[fd]
            writer.close()
            del OANOut._writers[fd]

            if writer.auth:
                url = writer.auth.url
                del OANOut._authorized[url]
                OANOut._out.clear([url])

        for connected_url, connected_fd in OANOut._connecting.items():
            if fd == connected_fd:
                log.info("connecting url removed (%s, %s)" % connected_url)
                del OANOut._connecting[connected_url]

                for url, poped, messages in OANOut._out.pop([connected_url], [], False):
                   OANOut.error_callback(connected_url, messages)

    @staticmethod
    def _run():
        inputs = []
        outputs = OANOut._fds

        OANOut._started.set()
        while OANServer._running:
            #time.sleep(0.2)
            OANLogCounter.begin("OANOut:Loop")

            pop_data = OANOut._out.pop(OANOut._authorized, OANOut._connecting,
                                       not outputs and OANServer._running)

            for url, poped, entry_data in pop_data:
                if poped:
                    writer = OANOut._authorized[url]
                    writer.push(entry_data)
                    fd = writer.fileno()

                    if (fd not in outputs):
                        outputs.append(fd)
                else:
                    OANOut._connect(url)

            if outputs:
                # log.info("OANOut: current %s" % outputs)
                # write output
                try:
                    readable, writable, exceptional = select.select(inputs, outputs, inputs)

                    for fd in writable:
                        writer = OANOut._writers[fd]
                        if writer.empty():
                            outputs.remove(fd)

                        try:
                            writer.handle()
                        except Exception, e:
                            log.info("handle_error: %s " % e)
                            outputs.remove(fd)
                            OANOut._close(fd)

                except Exception, e:
                    log.info("Error: %s on %s " % (e, outputs))
                    for fd in outputs[:]:
                        try:
                            readable, writable, exceptional = select.select(inputs, [fd], inputs, 0)
                        except Exception, e:
                            outputs.remove(fd)
                            OANOut._close(fd)

            OANLogCounter.end("OANOut:Loop")

        OANOut._close_all()
        log.info("OANOut: shutdown finished")

class OANIn:

    _readers = {}
    _fds = []
    _thread = None
    _started = None

    connect_callback = staticmethod(lambda fd, sock, auth : None)
    close_callback = staticmethod(lambda fd, sock, auth : None)
    accept_callback = staticmethod(lambda fd, sock : None)
    message_callback = staticmethod(lambda auth, messages : None)

    @staticmethod
    def start(notify_sock, listen_sock):
        OANIn._readers[notify_sock.fileno()] = OANRecvNotify(notify_sock)
        OANIn._readers[listen_sock.fileno()] = OANListen(listen_sock, OANIn._accept_occured)
        OANIn._fds = [listen_sock.fileno(), notify_sock.fileno()]
        OANIn._started = Event()
        OANIn._thread = Thread(target=OANIn._run, kwargs={})
        OANIn._thread.name="in"
        OANIn._thread.start()
        OANIn._started.wait()

    @staticmethod
    def authorized(fd, auth):
        OANIn._readers[fd].auth = auth

    @staticmethod
    def handshake(sock):
        if sock.fileno() in OANIn._readers:
            log.info("FD: fd already exists %s %s " % (sock.fileno(), OANIn._readers.keys()))
            raise OANNetworkError("fd already exists")

        reader = OANReader(sock,
                           OANIn._message_occured,
                           OANIn._connect_occured,
                           OANIn._close_occured)

        OANIn._readers[reader.fileno()] = reader
        OANIn._fds.append(reader.fileno())


    @staticmethod
    def shutdown():
        log.info("OANIn: shutdown begin")
        OANIn._thread.join()

    @staticmethod
    def _accept_occured(sock):
        #log.info("OANIn: accept %s " % sock.fileno())
        OANIn.accept_callback(sock)

    @staticmethod
    def _message_occured(fd, sock, auth, mess):
        try:
            #log.info("OANIn: messages %s count:%s " % (fd, len(messages)))
            OANIn.message_callback(auth, mess)
        except Exception, e:
            log.info(e)

    @staticmethod
    def _connect_occured(fd, sock, auth):
        try:
            #log.info("OANIn:_connect_occured %s" % fd)
            OANIn.connect_callback(fd, sock, auth)
        except Exception, e:
            log.info("Error: OANIn:_connect_occured %s %s" % (fd, e))

    @staticmethod
    def _close_occured(fd, sock, auth):
        try:
            #log.info("OANIn:_disconnect_occured %s" % fd)
            OANIn.close_callback(fd, sock, auth)
        except Exception, e:
            log.info("Error: OANIn:_close_occured %s %s" % (fd, e))

    @staticmethod
    def _close_all():
        for fd in OANIn._readers.keys()[:]:
            OANIn._close(fd)

    @staticmethod
    def _close(fd):
        reader = OANIn._readers[fd]
        del OANIn._readers[fd]
        OANIn._fds.remove(fd)
        reader.close()


    @staticmethod
    def _run():
        inputs = OANIn._fds
        outputs = []
        OANIn._started.set()
        while OANServer._running:
            OANLogCounter.begin("OANIn: loop")
            #time.sleep(0.5)
            try:
                readable, writable, exceptional = select.select(inputs, outputs, inputs)
                #log.info("OANIn: %s, %s, %s" % (readable, writable, exceptional))
                for fd in readable:
                    try:
                        if fd in OANIn._readers:
                            OANIn._readers[fd].handle()
                        else:
                            log.info("OANIn:missing reader on : %s " % fd)

                    except Exception, e:
                        log.info("OANIn:handle_error: %s " % e)
                        OANIn._close(fd)

            except Exception, e:
                log.info("Error: %s on %s " % (e, inputs))
                for fd in inputs[:]:
                    try:
                        readable, writable, exceptional = select.select([fd], outputs, [], 0)
                    except Exception, e:
                        OANIn._close(fd)

            OANLogCounter.end("OANIn: loop")

        OANIn._close_all()
        log.info("OANIn: shutdown finished")


class OANAuth():
    version = None
    oan_id = None
    host = None
    port = None
    url = None
    blocked = None

    def __init__(self, version = None, oan_id = None,
                 host = None, port = None, blocked = False):

        self.version = version
        self.oan_id = str(oan_id)
        self.host = host
        self.port = port
        self.blocked = blocked
        self.url = (host, port)

        log.info("OANAuth: %s %s:%s blocked: %s" % (
            self.oan_id, self.host, self.port, self.blocked))


class OANServer:
    host = None
    port = None
    auth = None

    _bind_socket = None
    _running = None
    _thread = None
    _started = None
    _connected = None
    _lock = Lock()

    connect_callback = staticmethod(lambda auth : None)
    close_callback = staticmethod(lambda auth : None)
    message_callback = staticmethod(lambda url, messages : None)
    error_callback = staticmethod(lambda url, messages : None)

    @staticmethod
    def start(auth):
        if OANServer._running:
            raise OANNetworkError("Already started")

        OANServer._connected = {}
        OANServer.auth = auth

        OANServer._bind_socket = OANServer._bind(OANServer.auth.host, OANServer.auth.port)
        OANServer._running = True

        client_notify_socket, server_notify_socket = OANServer._create_controller(
                OANServer.auth.host,
                OANServer.auth.port,
                OANServer._bind_socket)

        OANIn.close_callback = staticmethod(OANServer._in_close_occured)
        OANIn.connect_callback = staticmethod(OANServer._in_connect_occured)
        OANIn.message_callback = staticmethod(OANServer._message_occured)
        OANIn.accept_callback = staticmethod(OANServer._accept_occured)

        OANOut.close_callback = staticmethod(OANServer._out_close_occured)
        OANOut.connect_callback = staticmethod(OANServer._out_connect_occured)
        OANOut.accept_callback = staticmethod(OANServer._accept_occured)
        OANOut.error_callback = staticmethod(OANServer._out_error_occured)

        OANIn.start(server_notify_socket, OANServer._bind_socket)
        OANOut.start(client_notify_socket)

    @staticmethod
    def shutdown():
        if OANServer._running:
            OANServer._running = False
            OANOut.shutdown()
            OANIn.shutdown()
        else:
            raise OANNetworkError("Not started")

    @staticmethod
    def connected():
        return OANServer._connected.keys()[:]

    @staticmethod
    def push(urls, messages):
        OANOut.push(urls, messages)

    @staticmethod
    def _in_connect_occured(fd, sock, auth):
        log.info("OANServer: _in_connect_occured %s %s" % (fd, auth.url))
        try:
            if auth == None:
                raise OANNetworkError("auth is None")

            if auth.url not in OANServer._connected:
                OANOut.authorized(fd, auth)
                OANIn.authorized(fd, auth)
                OANServer._connected[auth.url] = auth
                OANServer.connect_callback(auth)
            else:
                log.info("Already connected %s %s closing socket" % (fd, auth.url))
                OANOut._writers[fd]._socket.close()

        except Exception, e:
            raise e

    @staticmethod
    def _out_connect_occured(fd, sock):
        log.info("OANServer: _out_connect_occured %s" % (fd))
        OANIn.handshake(sock)

    @staticmethod
    def _in_close_occured(fd, sock, auth):
        log.info("OANServer: _in_close_occured %s %s" % (fd, auth.url))
        try:
            if auth != None:
                del OANServer._connected[auth.url]
                OANServer.close_callback(auth)
            else:
                raise OANNetworkError("auth is None")

        except Exception, e:
            log.info("Error: %s" % e)

    @staticmethod
    def _accept_occured(sock):
        OANOut.handshake(sock, OANServer.auth)

    @staticmethod
    def _out_close_occured(fd, sock):
        log.info("OANServer: _out_close_occured %s" % (fd))

    @staticmethod
    def _out_error_occured(url, messages):
        log.info("OANServer: _out_error_occured %s %s" % (url, messages))
        OANServer.error_callback(url, messages)

    @staticmethod
    def _message_occured(auth, messages):
        #log.info("OANServer: _message_occured %s, %s" % (auth, fd))
        OANServer.message_callback(auth.url, messages)

    @staticmethod
    def _create_controller(host, port, bind_socket):
        client_socket = OANServer._connect_controller((host, port))
        readable, writable, exceptional = select.select([bind_socket.fileno()], [], [])
        server_socket, addr = bind_socket.accept()
        return (client_socket, server_socket)

    @staticmethod
    def _bind(host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(0)

        # try setting resuse address
        try:
            s.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR,
                s.getsockopt(socket.SOL_SOCKET,
                             socket.SO_REUSEADDR) | 1
                )
        except socket.error:
            pass

        # bind to host and port
        try:
            s.bind((host, port))
            s.listen(300)
            return s
        except socket.error, e:
            log.info("my socket err %s" % e)
            raise OANNetworkError(e)

    @staticmethod
    def _connect_controller(url):
        #todo: add errors from asyncore.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(0)
        err = s.connect_ex(url)

        err = s.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if err != 0:
            log.info("my socket err %s" % err)

        return s



