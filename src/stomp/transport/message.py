from stomp.const import HDR_CONTENT_LENGTH
from stomp.const import HDR_CONTENT_TYPE
from stomp.const import HDR_DESTINATION
from stomp.const import HDR_MESSAGE_ID
from stomp.const import HDR_SUBSCRIPTION
from stomp.exc import StompException


class Message(object):
    """A message received through the transport."""

    @property
    def sub(self):
        return self._sub

    @property
    def headers(self):
        return self._frame.headers

    @property
    def mid(self):
        return self._mid

    @property
    def body(self):
        return self._body

    @classmethod
    def fromframe(cls, connection, sub, frame):
        # MESSAGE frames SHOULD include a content-length header
        # and a content-type header if a body is present.
        assert frame.is_message()
        assert frame.has_header(HDR_DESTINATION)
        assert frame.has_header(HDR_MESSAGE_ID)
        assert frame.has_header(HDR_SUBSCRIPTION)
        content_type = frame.headers.get(HDR_CONTENT_TYPE)
        content_length = None
        if frame.has_header(HDR_CONTENT_LENGTH):
            try:
                content_length = int(frame.headers.get(HDR_CONTENT_LENGTH))
            except Exception:
                raise StompException("Invalid content-length header.")
        return cls(
            connection,
            sub,
            frame,
            connection.split_destinations(frame.headers[HDR_DESTINATION]),
            frame.headers[HDR_MESSAGE_ID],
            frame.body,
            content_type=content_type,
            content_length=content_length
        )

    def __init__(self, connection, sub, frame, destinations, mid, body, content_type=None,
        content_length=None):
        """Initialize a new :class:`Message` instance."""
        self._connection = connection
        self._sub = sub
        self._frame = frame
        self._mid = mid
        self._body = body
        self._content_type = content_type
        self._content_length = content_length

    def accept(self):
        """Notify the remote end that the message is accepted."""
        if self._frame.ack is not None:
            self._connection.send_frame(self._frame.ack)

    def reject(self):
        """Notify the remote end that the message is accepted."""
        if self._frame.nack is not None:
            self._connection.send_frame(self._frame.nack)
