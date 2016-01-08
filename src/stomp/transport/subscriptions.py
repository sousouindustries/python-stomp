import collections
import logging
import threading
try:
    import queue
except ImportError:
    import Queue as queue

from stomp.const import MESSAGE
from stomp.const import HDR_ID
from stomp.const import HDR_SUBSCRIPTION
from stomp.frames import UnsubscribeFrame
from stomp.transport.message import Message


class SubscriptionManager(object):
    """Manages subscriptions for a session with a ``STOMP`` server."""

    def __init__(self, session, connection, message_factory=None):
        self.session = session
        self.connection = connection
        connection.register_observer(self)
        self.subscriptions = collections.OrderedDict()
        self.logger = logging.getLogger('stomp.session')
        self.message_factory = message_factory or Message.fromframe

    def add(self, sid, destinations):
        """Register a new subscription."""
        assert sid not in self.subscriptions
        self.subscriptions[sid] = Subscription(
            self, sid, destinations)
        return self.subscriptions[sid]

    def notify(self, event, frame, *args, **kwargs):
        c = self.connection
        if event == c.EVNT_FRAME_RECV and frame.is_message():
            assert frame.command == MESSAGE
            assert frame.has_header(HDR_SUBSCRIPTION)
            assert frame.headers[HDR_SUBSCRIPTION] in self.subscriptions

            sid = frame.headers[HDR_SUBSCRIPTION]
            self.subscriptions[sid].put(
                self.message_factory(self.connection, self, frame)
            )
            raise c.DiscardFrame

        # if event == c.EVNT_RECONNECT:
        #     # On reconnect, re-subscribe for all subscriptions.
        #     for sub in self.subscriptions.values():
        #         sub.create(self.session.subscribe)

    def destroy(self, sid):
        """Destroy the :class:`Subscription` identified by `sid` and stop
        receiving messages for it.
        """
        if sid in self.subscriptions:
            sub = self.subscriptions.pop(sid)
            self.connection.send_frame(sub.unsubscribe_frame)
        

    def __iter__(self):
        return iter(self.subscriptions.values())


class Subscription(object):
    """Represents a subscription to one or more channels."""

    @property
    def unsubscribe_frame(self):
        frame = UnsubscribeFrame(with_receipt=True)
        frame.set_header(HDR_ID, self.sid)
        return frame

    @property
    def message_count(self):
        return self._messages_received

    @property
    def frame_count(self):
        return self._frame_count

    @property
    def messages(self):
        """Return all messages received by this subscription."""
        while True:
            try:
                yield self.queue.get(False)
            except queue.Empty:
                break
            else:
                self.queue.task_done()

    def __init__(self, manager, sid, destinations):
        self.manager = manager
        self.sid = sid
        self.destinations = destinations
        self.queue = queue.Queue()
        self.seen = collections.deque([], 1000)
        self._messages_received = 0
        self._frame_count = 0
        self._events = collections.OrderedDict()

    def put(self, msg):
        self._frame_count += 1
        if msg.mid not in self.seen:
            self._messages_received += 1
            self.seen.append(msg.mid)
            self.queue.put(msg)
            if self._events:
                self._events.pop(list(self._events.keys())[0]).set()

    def wait(self, timeout=None):
        """Block until a message has been received on this :class:`Subscription`.
        Return a boolean indicating if a message was received during the specified
        timeframe `timeout`.
        """
        t = threading.current_thread()
        if timeout is not None:
            timeout = int(timeout / 1000)
        self._events[t.ident] = threading.Event()
        return self._events[t.ident].wait(timeout)

    def destroy(self):
        """Stop receiving frames for this :class:`Subscription` and remove
        it from the registry.
        """
        return self.manager.destroy(self.sid)

    def __iter__(self):
        return iter(self.messages)
