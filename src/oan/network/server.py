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
    notify_count = 0


class OANMessageDictionary:
    _messages = None
    _lock = None
    _cond = None

    def __init__(self):
        self._messages = {}
        self._lock = Lock()
        self._cond = Condition(self._lock)

    def push(self, urls, messages):
        with self._lock:
            notify = (len(self._messages) == 0)

            for url in urls:
                if url in self._messages:
                    self._messages[url].extend(messages)
                else:
                    self._messages[url] = messages[:]

            if notify:
                self._cond.notify()

    def interrupt(self):
        with self._lock:
            self._cond.notify()

    def keys(self, block = True):
        with self._lock:
            if (block and len(self._messages) == 0):
                self._cond.wait()

            return self._messages.keys()[:]

    def clear(self, url):
        with self._lock:
            if url in self._messages:
                del self._messages[url]

    def pop(self, url):
        with self._lock:
            if url in self._messages:
                mess = self._messages[url]
                del self._messages[url]
                return mess

            return None

class OANController:

    _client_socket = None
    _server_socket = None
    _buffer = None
    _connected = None

    def __init__(self, client_socket, server_socket):
        self._connected = False
        self._client_socket = client_socket
        self._server_socket = server_socket
        self._buffer = ""

    def fileno(self):
        return self._server_socket.fileno()

    def connected(self):
        return self._connected

    def handle_connect(self):
        self._connected = True

    def close(self):
        self._server_socket.close()
        self._client_socket.close()

    def handle_write(self):
        self._client_socket.send('\n')

    def handle_read(self):
        data = self._server_socket.recv(128)
        #if data:
        #    log.info("OANController:handle_read: [%s]" % (data))

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
        return "counter:%s total:%s avg: %s min:%s max:%s " % (
            self.counter,
            self.total_elapsed,
            self.total_elapsed / self.counter,
            self.min_elapsed,
            self.max_elapsed)

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
            ret += "%s: %s\n" % (key, str(entry))

        return ret


class OANReader:

    _socket = None
    _buffer = None
    _buffer_size = None
    _frame_size = None
    _connected = None

    def __init__(self, socket):
        self._socket = socket
        self._buffer = deque()
        self._buffer_size = 0
        self._frame_size = 0
        self._connected = False

    def fileno(self):
        return self._socket.fileno()

    def connected(self):
        return self._connected

    def close(self):
        self._socket.close()

    def handle_connect(self):
        self._connected = True

    def handle_read(self):
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
        OANCounter.in_count += len(ret)
        return ret

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

    _socket = None
    _buffer = None
    _data = None
    _connected = None
    _current = None
    _size = None

    def __init__(self, socket):
        self._connected = False
        self._socket = socket
        self._buffer = []
        self._current = 0
        self._size = 0
        self._data = ""

    def connected(self):
        return self._connected

    def fileno(self):
        return self._socket.fileno()

    def close(self):
        self._socket.close()

    def push(self, messages):
        for message in messages:
            self._buffer.append(message)
            self._size += len(message)

        #log.info(self._buffer)

    def empty(self):
        return len(self._buffer) == 0 and len(self._data) == self._current

    def handle_connect(self):
        self._connected = True

    def handle_write(self):

        OANLogCounter.begin("handle_write")

        # fill buffer
        if len(self._buffer) > 0 and len(self._data) == self._current:
            tmp = []
            tmp.append(pack('i', self._size + (len(self._buffer)-1)))
            tmp.append('\n'.join(self._buffer))
            OANCounter.out_count += len(self._buffer)

            self._data = ''.join(tmp)
            self._current = 0
            self._size = 0
            self._buffer = []

        ## send data
        if self._data:
            sent = self._socket.send(self._data[self._current:self._current + 64000])
            self._current += sent
            OANCounter.out_bytes += sent
            OANCounter.out_writes += 1

        OANLogCounter.end("handle_write")



class OANOut:

    _out = OANMessageDictionary()
    _writers = {}
    _fds = []
    _thread = None
    _started = None
    _controller = None

    connect_callback = staticmethod(lambda fd : None)
    disconnect_callback = staticmethod(lambda fd : None)

    @staticmethod
    def start(controller):
        OANOut._controller = controller
        OANOut._writers[controller.fileno()] = controller
        OANOut._fds.append(controller.fileno())

        OANOut._started = Event()
        OANOut._thread = Thread(target=OANOut._run, kwargs={})
        OANOut._thread.name="out"
        OANOut._thread.start()
        OANOut._started.wait()

    def connect(url):
        sock = OANOut._connect(url)
        OANOut._add(OANWriter(sock))

    @staticmethod
    def shutdown():
        OANOut._out.interrupt()
        OANOut._thread.join()

    @staticmethod
    def push(urls, messages):
        OANOut._out.push(urls, messages)

    @staticmethod
    def add(sock):
        writer = OANWriter(sock)
        OANOut._writers[writer.fileno()] = writer
        OANOut._fds.append(int(writer.fileno()))

    @staticmethod
    def _connect_occured(fd):
        try:
            #log.info("OANOut:_connect_occured %s" % fd)
            OANOut.connect_callback(fd)
        except Exception, e:
            log.info("_connect_occured %s %s" % (fd, e))

    @staticmethod
    def _disconnect_occured(fd):
        try:
            #log.info("OANOut:_disconnect_occured %s" % fd)
            OANOut.disconnect_callback(fd)
        except Exception, e:
            log.info("_disconnect_occured %s %s" % (fd, e))

    @staticmethod
    def _close_all():
        for fd in OANOut._writers.keys()[:]:
            OANOut._close(fd)

    @staticmethod
    def _close(fd):
        if fd in OANOut._writers:
            OANOut._writers[fd].close()
            del OANOut._writers[fd]

        OANOut._disconnect_occured(fd)
        OANOut._out.clear(fd)

    @staticmethod
    def _run():
        inputs = []
        outputs = []
        OANOut._started.set()
        while OANServer._running:
            #log.info("OANOut: loop")

            # only wait if outputs is empty
            for key in OANOut._out.keys(block = (len(outputs) == 0 and OANServer._running)):
                if (key not in outputs):
                    outputs.append(key)

            if len(outputs) > 0:
                #log.info("OANOut: current %s" % outputs)
                # write output
                try:
                    readable, writable, exceptional = select.select(inputs, outputs, inputs)

                    for fd in writable:
                        writer = OANOut._writers[fd]

                        if not writer.connected():
                            OANOut._controller.handle_write()
                            OANOut._connect_occured(fd)
                            writer.handle_connect()

                        if writer.empty():
                            data = OANOut._out.pop(fd)
                            #log.info("OANOut: data %s" % data)
                            if data:
                                writer.push(data)
                            else:
                                outputs.remove(fd)

                        try:
                            writer.handle_write()
                        except Exception, e:
                            log.info("handle_write error: %s " % e)
                            outputs.remove(fd)
                            OANOut._close(fd)

                except Exception, e:
                    log.info("Error: %s on %s " % (e, outputs))
                    for fd in outputs[:]:
                        try:
                            readable, writable, exceptional = select.select(inputs, [fd], inputs, 0)
                        except Exception, e:
                            log.info("Found error sock: %s " % fd)
                            outputs.remove(fd)
                            OANOut._close(fd)

        OANOut._close_all()
        log.info("OANOut: shutdown finished")

class OANIn:

    _controller = None
    _readers = {}
    _fds = []
    _thread = None
    _started = None
    _listen_sock = None
    connect_callback = staticmethod(lambda fd : None)
    disconnect_callback = staticmethod(lambda fd : None)
    accept_callback = staticmethod(lambda socket : None)
    message_callback = staticmethod(lambda fd, messages : None)

    @staticmethod
    def start(controller, listen_sock):
        OANIn._controller = controller
        OANIn._listen_sock = listen_sock
        log.info("listen on: %s " % listen_sock.fileno())

        OANIn._readers[controller.fileno()] = controller

        OANIn._fds = [listen_sock.fileno(), controller.fileno()]
        OANIn._started = Event()
        OANIn._thread = Thread(target=OANIn._run, kwargs={})
        OANIn._thread.name="in"
        OANIn._thread.start()
        OANIn._started.wait()

    @staticmethod
    def add(sock):
        reader = OANReader(sock)
        OANIn._readers[reader.fileno()] = reader
        OANIn._fds.append(reader.fileno())

    @staticmethod
    def shutdown():
        OANIn._thread.join()

    @staticmethod
    def _accept_occured():
        sock, addr = OANIn._listen_sock.accept()
        sock.setblocking(0)
        log.info("OANIn: accept %s " % sock.fileno())
        OANIn.accept_callback(sock)

    @staticmethod
    def _message_occured(fd, messages):
        try:
            #log.info("OANIn: messages %s count:%s " % (fd, len(messages)))
            OANIn.message_callback(fd, messages)
        except Exception, e:
            log.info(e)

    @staticmethod
    def _connect_occured(fd):
        try:
            #log.info("OANIn:_connect_occured %s" % fd)
            OANIn.connect_callback(fd)
        except Exception, e:
            log.info("OANIn:_connect_occured %s %s" % (fd, e))

    @staticmethod
    def _disconnect_occured(fd):
        try:
            #log.info("OANIn:_disconnect_occured %s" % fd)
            OANIn.disconnect_callback(fd)
        except Exception, e:
            log.info("OANIn:_disconnect_occured %s %s" % (fd, e))


    @staticmethod
    def _close_all():
        for fd in OANIn._readers.keys()[:]:
            OANIn._close(fd)

        OANIn._listen_sock.close()

    @staticmethod
    def _close(fd):
        OANIn._readers[fd].close()
        OANIn._fds.remove(fd)
        del OANIn._readers[fd]
        OANIn._disconnect_occured(fd)

    @staticmethod
    def _run():
        outputs = []
        OANIn._started.set()
        while OANServer._running:
            #log.info("OANIn: loop")
            #time.sleep(0.5)
            #log.info("OANIn current: %s" % (OANIn._fds))
            try:
                readable, writable, exceptional = select.select(OANIn._fds, outputs, OANIn._fds)
                #log.info("OANIn: %s, %s, %s" % (readable, writable, exceptional))
                for fd in readable:
                    if (fd == OANIn._listen_sock.fileno()):
                        OANIn._accept_occured()
                    else:
                        reader = OANIn._readers[fd]
                        if not reader.connected():
                            reader.handle_connect()
                            OANIn._connect_occured(fd)

                        try:
                            mess = reader.handle_read()

                            if reader.fileno() != OANIn._controller.fileno():
                                if len(mess) > 0:
                                    OANIn._message_occured(fd, mess)

                        except Exception, e:
                            log.info("handle_read error: %s " % e)
                            OANIn._close(fd)


            except Exception, e:
                log.info("Error: %s on %s " % (e, OANIn._fds))
                for fd in OANIn._fds[:]:
                    try:
                        readable, writable, exceptional = select.select([fd], outputs, [], 0)
                    except Exception, e:
                        log.info("Found error sock: %s " % fd)
                        OANIn._close(fd)

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
    _controller = None
    _running = None
    _thread = None
    _started = None
    _connected = None
    _handshaked = None

    connect_callback = staticmethod(lambda auth : None)
    close_callback = staticmethod(lambda auth, messages : None)
    message_callback = staticmethod(lambda url, messages : None)
    error_callback = staticmethod(lambda reader, messages : None)

    @staticmethod
    def start(auth):
        if OANServer._running:
            raise OANNetworkError("Already started")

        OANServer._connected = {}
        OANServer._handshaked = {}

        OANServer.auth = auth

        OANServer._bind_socket = OANServer._bind(OANServer.auth.host, OANServer.auth.port)
        OANServer._running = True

        OANServer._controller = OANServer._create_controller(
                OANServer.auth.host,
                OANServer.auth.port,
                OANServer._bind_socket)

        OANIn.disconnect_callback = staticmethod(OANServer._disconnect_occured)
        OANIn.connect_callback = staticmethod(OANServer._connect_occured)
        OANIn.message_callback = staticmethod(OANServer._message_occured)
        OANIn.accept_callback = staticmethod(OANServer._accept_occured)

        OANOut.disconnect_callback = staticmethod(OANServer._disconnect_occured)
        OANOut.connect_callback = staticmethod(OANServer._connect_occured)

        OANIn.start(OANServer._controller, OANServer._bind_socket)
        OANOut.start(OANServer._controller)

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
        return OANServer._connected.keys()

    @staticmethod
    def connect(urls):
        for url in urls:
            if url == OANServer.auth.url:
                raise OANNetworkError("Can not connect to your self")

            if url not in OANServer._connected:
                sock = OANServer._connect(url)
                OANServer._add_socket(sock)
                OANServer._connected[url] = sock.fileno()
                log.info("OANServer: connected %s %s" % (url, OANServer._connected[url]))

    @staticmethod
    def push(urls, messages):
        fds = []
        #lock
        for url in urls:
            #todo the url may be missing in connected
            fd = OANServer._connected[url]
            fds.append(fd)

        OANOut.push(fds, messages)

    @staticmethod
    def _send_handshake(sock):
        OANOut.push([sock.fileno()], ["OAN %s %s %s" % (
            OANServer.auth.oan_id,
            OANServer.auth.host,
            OANServer.auth.port)]
        )

    @staticmethod
    def _validate_handshake(fd, message):
        log.info("_validate_handshake %s" % message)
        try:
            protocol, oan_id, host, port = message.split(' ')
            auth = OANAuth(protocol, oan_id, host, int(port), False)
            OANServer.connect_callback(auth)
            OANServer._handshaked[fd] = auth
            OANServer._connected[auth.url] = fd

            return True

        except Exception, e:
            raise e

        return False

    @staticmethod
    def _connect_occured(fd):
        pass

    @staticmethod
    def _disconnect_occured(fd):
        try:
            if fd in OANServer._handshaked:
                auth = OANServer._handshaked[fd]
                del OANServer._connected[auth.url]
                del OANServer._handshaked[fd]
                OANServer.close_callback(auth, [])
            else:
                for url, v in OANServer._connected.items()[:]:
                    if v == fd:
                        log.info("disconnect without handshake: %s" % fd)
                        del OANServer._connected[url]

        except Exception, e:
            log.info("Error: %s" % e)

    @staticmethod
    def _add_socket(sock):
        OANIn.add(sock)
        OANOut.add(sock)
        OANServer._send_handshake(sock)

    @staticmethod
    def _accept_occured(sock):
        OANServer._add_socket(sock)

    @staticmethod
    def _message_occured(fd, messages):

        if fd not in OANServer._handshaked:
            if OANServer._validate_handshake(fd, messages[0]):
                del messages[0]
            else:
                log.info("invalid handshake")

        if len(messages) > 0:
            auth = OANServer._handshaked[fd]
            url = (auth.host, auth.port)
            OANServer.message_callback(url, messages)

    @staticmethod
    def _create_controller(host, port, bind_socket):

        client_socket = OANServer._connect((host, port))
        readable, writable, exceptional = select.select([bind_socket.fileno()], [], [])
        server_socket, addr = bind_socket.accept()
        return OANController(client_socket, server_socket)

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
    def _connect(url):
        #todo: add errors from asyncore.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(0)
        err = s.connect_ex(url)

        err = s.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if err != 0:
            log.info("my socket err %s" % err)
            raise OANNetworkError("socket error %s" % err)

        return s



