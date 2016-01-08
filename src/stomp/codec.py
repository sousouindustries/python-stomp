import collections
import copy
import functools
import operator

from stomp.const import *
from stomp.exc import MalformedFrame
from stomp.exc import InvalidCommandType
from stomp.frames import Frame


class Codec(object):
    """Encodes and decodes ``STOMP`` frames."""
    encoding = "utf-8"

    def __init__(self, eol=None):
        self.eol = ((CR+LF) if (eol==CR) else LF)\
            .encode(self.encoding)

    def consume_buffer(self, buf):
        """Consume all frames in a file-like object until EOF is
        reached.
        """
        while True:
            try:
                yield Frame(*self.decode(buf))

                # The buffer might contain multiple frames, hearbeats.
            except EOFError:
                break

    def decode(self, buf):
        """Decodes the ``STOMP`` frame contained in `buf`."""
        decoder = Decoder(self, buf)
        return decoder.decode()

    def encode(self, command, headers, body=None, encode=False):
        """Encode a ``STOMP`` frame.

        Args:
            command: a string specifying the command. Must be
                one of :data:`~stomp.const.FRAME_TYPES`.
            headers: a list of key/value pairs representing the
                headers.
            body: a string holding the message body; only applicable
                for ``MESSAGE`` frames.

        Returns:
            str
        """
        headers = copy.deepcopy(headers)
        if command not in FRAME_TYPES:
            raise InvalidCommandType("Not a STOMP command: " + command)
        nodes = [command.encode(self.encoding)]

        if bool(body):
            assert command in (SEND, MESSAGE, ERROR)
            headers.insert(0, ['content-length', str(len(body))])

        for key, value in headers:
            nodes.extend([self.eol, self.encode_header(command, key, value)])

        nodes.extend([self.eol, self.eol])
        if body is not None:
            if not isinstance(body, bytes):
                body = body.encode(self.encoding)
            nodes.append(body)

        nodes.append(NULL.encode(self.encoding))
        return functools.reduce(operator.add, nodes)

    def encode_header(self, command, key, value):
        """Encode the header for a ``STOMP`` frame."""
        key = self._escape(command, key)
        value = self._escape(command, value)
        return ':'.join([key, value]).encode(self.encoding)

    def _escape(self, command, value):
        # Escaping is needed to allow header keys and values to contain those
        # frame header delimiting octets as values. The CONNECT and CONNECTED
        # frames do not escape the carriage return, line feed or colon octets
        # in order to remain backward compatible with STOMP 1.0.

        # C style string literal escapes are used to encode any carriage return,
        # line feed or colon that are found within the UTF-8 encoded headers.
        # When decoding frame headers, the following transformations MUST be
        # applied:

        # - \r (octet 92 and 114) translates to carriage return (octet 13)
        # - \n (octet 92 and 110) translates to line feed (octet 10)
        # - \c (octet 92 and 99) translates to : (octet 58)
        # - \\ (octet 92 and 92) translates to \ (octet 92)
        #
        # (STOMP 1.2 specification)
        value = value.replace(BS, BS + BS)
        if command not in [CONNECT, CONNECTED]:
            value = value\
                .replace(CR, ESC + chr(114))\
                .replace(LF, ESC + chr(110))\
                .replace(COL, ESC + chr(99))

        return value

    def unescape(self, command, value):
        if command not in [CONNECT, CONNECTED]:
            value = value.replace(ESC + chr(114), CR)\
                .replace(ESC + chr(110), LF)\
                .replace(ESC + chr(99), COL)

        return value.replace(ESC + BS, BS)


class Decoder(object):

    def __init__(self, codec, buf):
        self.buf = buf
        self.content_length = None
        self.command = ''
        self.body = b''
        self.raw_headers = ''
        self.eol_count = 0
        self.headers = []
        self.codec = codec

    def decode(self):
        """Decodes a ``STOMP`` frame contained in :attr:`Decoder.buf`."""
        # If the buffer starts with a newline, we **probably**
        # have either, reached the end of the stream or received
        # a buffer with one or more heartbeats preceding the frame.
        octet_prime = self.buf.read(1).decode(self.codec.encoding)
        while octet_prime == LF:
            octet_prime = self.buf.read(1).decode(self.codec.encoding)

        if not octet_prime:
            raise EOFError

        self.buf.seek(self.buf.tell() - 1)
        while True:
            octet = self.buf.read(1).decode(self.codec.encoding)
            if not octet:
                break
            if octet == LF:
                break
            if octet == CR:
                continue
            self.command += octet

        if self.command not in FRAME_TYPES:
            raise InvalidCommandType("Not a STOMP command: " + self.command)

        # Read the buffer until we encounter two EOLs. This is where
        # the message body starts.
        while True:
            octet = self.buf.read(1).decode(self.codec.encoding)
            if not octet:
                raise MalformedFrame("Unexpected end of byte-stream.")

            if self.raw_headers and (self.raw_headers[-1] == LF) and (octet == LF):
                break

            if octet == CR:
                continue

            self.raw_headers += octet

        self._parse_headers()
        self._parse_body()
        return self.command, self.headers, self.body

    def _parse_headers(self):
        headers = collections.OrderedDict()
        f = functools.partial(self.codec.unescape, self.command)
        for pair in filter(bool, self.raw_headers.split(LF)):
            # Carriage return is optional, so we strip it here.
            key, val = map(f, pair.rstrip(CR).split(':'))

            # If a client or a server receives repeated frame header entries,
            # only the first header entry SHOULD be used as the value of
            # header entry. Subsequent values are only used to maintain a
            # history of state changes of the header and MAY be ignored.
            if key in headers:
                continue

            headers[key] = val

        if 'content-length' in headers:
            try:
                l = headers['content-length']
                self.content_length = int(l)
            except Exception:
                raise MalformedFrame("Malformed `content-length` header: " + l)

        delattr(self, 'raw_headers')
        self.headers = list([tuple(x) for x in headers.items()])

    def _parse_body(self):
        if self.content_length:
            self.body = self.buf.read(self.content_length)
            octet = self.buf.read(1).decode(self.codec.encoding)
            if octet != NULL:
                raise MalformedFrame("Frame body too large.")
        else:
            while True:
                octet = self.buf.read(1)
                if not octet or (octet.decode(self.codec.encoding) == NULL):
                    break
                self.body += octet


