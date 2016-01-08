import logging
import uuid

from stomp.const import HDR_ACK
from stomp.const import HDR_ID
from stomp.const import HDR_DESTINATION
from stomp.const import HDR_HEARBEAT
from stomp.const import HDR_VERSION
from stomp.frames import SubscribeFrame
from stomp.transport.subscriptions import SubscriptionManager


class Session(object):
    """Represents a session with the ``STOMP`` server, established
    with the ``CONNECTED`` frame.
    """

    @classmethod
    def fromframe(cls, connection, frame):
        """Create a new :class:`Session` using a :class:`~stomp.frames.Frame`
        instance.
        """
        send_hb = recv_hb = 0
        if frame.has_header(HDR_HEARBEAT):
            send_hb, recv_hb = map(int, frame.headers[HDR_HEARBEAT].split(','))
        version = frame.headers[HDR_VERSION]
        return cls(connection, version, send_hb, recv_hb)

    def __init__(self, connection, version, send_hb=None, recv_hb=None, **extra):
        """Initialize a new :class:`Session` instance.

        Args:
            connection: a :class:`~stomp.transport.Connection` instance.
            version: the ``STOMP`` protocol version that will be used
                in this session.
            send_hb: an unsigned integer indicating the frequency at
                which the client must send heartbeats.
            recv_hb: an unsigned integer indicating the frequency at
                which the server will send heartbeats.
            **extra: extra parameters sent by the server.
        """
        self.connection = connection
        self.version = version
        self.send_hb = send_hb
        self.recv_hb = recv_hb
        self.params = extra or {}
        self.subscriptions = SubscriptionManager(self, self.connection,
            message_factory=connection.message_factory)
        self.logger = logging.getLogger('stomp.session')

    def subscribe(self, destinations, **kwargs):
        """Subscribe to the specified `destination`.

        Args:
            destinations: a string specifying a single
                destination; or a list holding multiple
                destinations.
            ack_mode: specifies the acknowledgement mode
                for incoming frames. Must be one of ``auto``,
                ``client`` or ``client-individual``.

        Returns:
            :class:`Subscription`
        """
        if not isinstance(destinations, list):
            destinations = [destinations]

        # Use an exclusive lock on the connection so we can check
        # if the SUBSCRIBE frame leads to an ERROR. In that case,
        # do not add the subscription to the registry so all
        # subscriptions can always be restored when the connection
        # is reestablished.
        sid = kwargs.pop('_sid', uuid.uuid4().hex)

        headers = self.get_subscription_headers(sid, destinations, **kwargs)
        frame = SubscribeFrame(list(headers.items()))
        with self.connection.claim():
            self.connection.send_frame(frame)
            self.connection.update()

        sub = self.subscriptions.add(sid, destinations)
        _ = (sid, frame.headers[HDR_DESTINATION])
        self.logger.info(
            "Subscribed to {1} (id={0})".format(*_))

        return sub

    def get_subscription_headers(self, sid, destinations, ack_mode=None, **kwargs):
        headers = kwargs.pop('extra_headers', None) or {}
        headers.update({
            HDR_ID: sid,
            HDR_DESTINATION: self.connection.join_destination(destinations)
        })
        if ack_mode is not None:
            headers[HDR_ACK] = ack_mode
        return headers

    def __repr__(self):
        return "<Session: STOMP {0}>".format(self.version)

    def __iter__(self):
        return iter(self.subscriptions)
