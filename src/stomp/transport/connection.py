import collections
import errno
import io
import select
import socket
import time
import threading
try:
    import queue
except ImportError:
    import Queue as queue

from stomp.codec import Codec
from stomp.const import ACCEPT_VERSIONS
from stomp.exc import StompException
from stomp.exc import FrameNotConfirmed
from stomp.frames import Frame
from stomp.frames import ConnectFrame
from stomp.frames import DisconnectFrame
from stomp.transport.receiptmanager import ReceiptManager
from stomp.transport.session import Session


class Connection(object):
    """Manages the connection to the ``STOMP`` server."""
    buf_size = 1024
    DiscardFrame = type('DiscardFrame', (Exception,), {})
    EVNT_FRAME_RECV = 'frame_received'
    EVNT_FRAME_SENT = 'frame_sent'
    EVNT_RECONNECT  = 'reconnect'

    @staticmethod
    def get_connect_frame(settings):
        headers = {
            'accept-version': ACCEPT_VERSIONS,
            'host': settings.vhost,
            'login': settings.username,
            'passcode': settings.password
        }
        if settings.send_hb or settings.send_hb:
            headers.update({
                'heart-beat': "{send_hb},{recv_hb}".format(
                    send_hb=settings.send_hb,
                    recv_hb=settings.recv_hb
                )
            })
        return ConnectFrame(list(headers.items()))

    @property
    def message_factory(self):
        return self.settings.message_factory

    def __init__(self, settings, lock=None):
        self.settings = settings
        self.lock = lock or threading.RLock()
        self.exclusive = threading.RLock()
        self.codec = Codec()

        # Setup asynchronous frame receiving.
        self.frames = queue.Queue()
        self.thread = threading.Thread(target=self.__main__)
        self.thread.daemon = True


        # Keep track of ingress and egress data for heartbeating.
        self.data_in = collections.deque([], 10)
        self.data_out = collections.deque([], 10)

        self._must_stop = False
        self._observers = []
        self._error = None
        self._max_retries = 10
        self._receipt_timeout = 1000
        self._receipts = ReceiptManager(self)

    def claim(self):
        """Return a context-manager that exclusively claims all I/O
        for this :class:`Connection`.
        """
        return self.lock

    def join_destination(self, destinations):
        """Joins a list of destination using the destination separator
        specified in the configuration.
        """
        return self.settings.dest_separator.join(destinations)\
            if isinstance(destinations, (list, tuple))\
            else destinations

    def split_destinations(self, destinations):
        return destinations.split(self.settings.dest_separator)

    def register_observer(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def notify_observers(self, event, **kwargs):
        for observer in self._observers:
            observer.notify(event, **kwargs)

    def must_heartbeat(self):
        """Return a boolean indicating if the client must send a heartbeat
        to the ``STOMP`` server.
        """
        hb = False
        if self.data_out:
            delta_t = int(time.time() * 1000) - self.data_out[-1]
            hb |= delta_t > self.settings.send_hb

        return hb

    def connect(self):
        """Connect the :class:`Connection` instance to the remote
        ``STOMP`` server.
        """
        self._connect_socket()
        self.send_frame(self.get_connect_frame(self.settings))
        self.thread.start()
        response = self.recv_frame(True, 2500)
        return Session.fromframe(self, response)

    def update(self):
        """Read all data from the socket and add the frames to the frame
        buffer.
        """
        with self.lock:
            octet_count = 0
            buf = io.BytesIO()
            while True:
                # Note: this approach assumes that the server always
                # sends us complete frames.
                try:
                    buf.write(self.recv(self.buf_size))
                except EnvironmentError as e:
                    if e.errno != errno.EAGAIN: raise
                    break

            buf.seek(0)

        # Continue to the next iteration if there are no
        # octets to read.
        for frame in self.codec.consume_buffer(buf):
            if frame.is_error():
                raise StompException.fromframe(frame)
            try:
                self.notify_observers(self.EVNT_FRAME_RECV, frame=frame)
            except self.DiscardFrame:
                pass
            self.frames.put(frame)

    def send_frame(self, frame):
        """Sends a ``STOMP`` frame, represented as a :class:`
        ~stomp.frames.Frame` instance, to the remote server.
        """
        self.notify_observers(self.EVNT_FRAME_SENT, frame=frame)
        raw = self.codec.encode(*frame, encode=True)
        attempts = 0
        #print(raw)
        while True:
            result = self.send(raw)
            if not frame.expects_receipt():
                break

            try:
                self._receipts.wait(frame.receipt_id, self._receipt_timeout)
                break
            except FrameNotConfirmed:
                attempts += 1
                if attempts > self._max_retries:
                    raise

        return result

    def send(self, seq):
        """Send a byte-sequence to the remote server."""
        with self.lock:
            #if len(seq) > 1:
            #    print(seq)
            self.data_out.append(int(time.time() * 1000))
            return self.socket.send(seq)

    def recv(self, n):
        """Receive at maximum ``n`` amount of bytes from the server."""
        with self.lock:
            seq = self.socket.recv(n)
            if seq:
                self.data_in.append(int(time.time() * 1000))
            #print(seq)
        return seq

    def recv_frame(self, block=True, timeout=None):
        """Receive one frame from the ``STOMP`` server."""
        if timeout:
            timeout = int(timeout / 1000)
        try:
            frame = self.frames.get(block, timeout)
            self.frames.task_done()
        finally:
            if self._error:
                raise self._error

        return frame

    def close(self):
        """Sends the ``DISCONNECT`` frame to the ``STOMP``
        server and closes the socket.
        """
        with self.lock:
            self.send_frame(DisconnectFrame())
            self._close_connection()

    def _connect_socket(self):
        # TODO: IPv6 support!!!!!!!!!
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.settings.host, self.settings.port))
        self.socket.setblocking(0)

    def _close_connection(self):
        self._stop()
        self.socket.close()

    def _stop(self):
        self._must_stop = True

    def _is_stopped(self):
        return self._must_stop

    def __main__(self):
        # A main event loop draining data from the socket and putting it
        # in a buffer.
        self._must_stop = False
        while True:
            if self._is_stopped():
                break

            with self.lock:
                # Send a newline to satisfy the servers' heartbeat
                # expectations, if necessary.
                if self.must_heartbeat():
                    self.send('\n'.encode())

                try:
                    self.update()
                except StompException as e:
                    self._close_connection()
                    self._error = e

            time.sleep(0.02)
