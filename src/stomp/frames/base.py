import functools
import uuid

from stomp.const import ACK
from stomp.const import NACK
from stomp.const import ERROR
from stomp.const import MESSAGE
from stomp.const import HDR_ACK
from stomp.const import HDR_ID
from stomp.const import HDR_RECEIPT
from stomp.const import HDR_RECEIPT_ID


class Frame(object):
    """The base class for all ``STOMP`` frames."""

    @property
    def receipt_id(self):
        return self.headers.get(HDR_RECEIPT)\
            or self.headers.get(HDR_RECEIPT_ID)

    @property
    def ack(self):
        if HDR_ACK not in self.headers:
            return None

        headers = [
            (HDR_ID, self.headers[HDR_ACK]),
            (HDR_RECEIPT, uuid.uuid4().hex)
        ]
        return Frame(ACK, headers)

    @property
    def nack(self):
        if HDR_ACK not in self.headers:
            return None

        headers = [
            (HDR_ID, self.headers[HDR_ACK]),
            (HDR_RECEIPT, uuid.uuid4().hex)
        ]
        return Frame(NACK, headers)

    @property
    def headers(self):
        return dict(self.__headers)

    @property
    def command(self):
        return self.__command

    @property
    def body(self):
        return self.__body

    @classmethod
    def factory(cls, command):
        return functools.partial(cls, command)

    def __init__(self, command, headers=None, body=None, with_receipt=False):
        self.__command = command
        self.__headers = headers or []
        self.__body = body
        if with_receipt:
            self.__headers.append([HDR_RECEIPT, uuid.uuid4().hex])

    def expects_receipt(self):
        """Return a boolean indicating if the :class:`Frame` expects
        a receipt.
        """
        return HDR_RECEIPT in self.headers

    def is_error(self):
        """Return a boolean indicating if the frame is an ``ERROR``."""
        return self.__command == ERROR

    def is_message(self):
        """Return a boolean indicating if the frame is an ``ERROR``."""
        return self.__command == MESSAGE

    def has_header(self, header_name):
        """Return a boolean indicating if the given header was specified on the
        frame.
        """
        return header_name in self.headers

    def set_header(self, name, value):
        self.__headers.append((name, value))

    def __iter__(self):
        return iter((self.__command, self.__headers, self.__body))

    def __repr__(self):
        return "<Frame: {0}>".format(self.__command)
