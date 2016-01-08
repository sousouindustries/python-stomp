import copy
import io
import re
import unittest

from stomp.const import CR
from stomp.const import LF
from stomp.const import SEND
from stomp.codec import Codec
from stomp.exc import MalformedFrame
from stomp.exc import InvalidCommandType
from stomp.exc import FatalException


class DecodingTestCase(unittest.TestCase):
    default_message = {
        'command': SEND,
        'headers': [
            ('destination', 'topic://test'),
            ('auto' + LF + 'escape', 'test')
        ],
        'body': "Hello world!"
    }

    def setUp(self):
        self.codec = Codec()
        self.msg = self.codec.encode(**self.default_message)

    def test_decode_command(self):
        command, headers, body = self.codec.decode(io.BytesIO(self.msg))
        self.assertEqual(command, self.default_message['command'])

    def test_decode_headers(self):
        command, headers, body = self.codec.decode(io.BytesIO(self.msg))
        headers = dict(headers)
        headers.pop('content-length')
        self.assertEqual(headers, dict((self.default_message['headers'])))

    def test_decode_body(self):
        command, headers, body = self.codec.decode(io.BytesIO(self.msg))
        self.assertEqual(body.decode(), self.default_message['body'])

    def test_decode_without_content_length(self):
        msg = re.sub('content-length\:.*\n', '', self.msg.decode(),
            re.DOTALL|re.MULTILINE).encode()
        command, headers, body = self.codec.decode(io.BytesIO(msg))
        self.assertEqual(body.decode(), self.default_message['body'])

    def test_decode_raises_with_trailing_data(self):
        msg = self.msg[:-1] + b'a'
        buf = io.BytesIO(msg)
        self.assertRaises(MalformedFrame, self.codec.decode, buf)

    def test_decode_with_carriage_return_command(self):
        codec = Codec(eol=CR)
        body = "Hello world!"
        msg = codec.encode(SEND, [], body=body)
        command, headers, body = codec.decode(io.BytesIO(msg))
        self.assertEqual(command, self.default_message['command'])

    def test_decode_with_invalid_command_raises(self):
        msg = re.sub('^SEND', 'FOO', self.msg.decode()).encode()
        buf = io.BytesIO(msg)
        self.assertRaises(FatalException, self.codec.decode, buf)

        buf.seek(0)
        self.assertRaises(InvalidCommandType, self.codec.decode, buf)

    def test_decode_partial_raises(self):
        msg = b'MESSAGE'
        buf = io.BytesIO(msg)
        self.assertRaises(MalformedFrame, self.codec.decode, buf)

    def test_decode_multiple_headers(self):
        params = copy.deepcopy(self.default_message)
        params['headers'].append(('destination','foo'))
        msg = self.codec.encode(**params)
        buf = io.BytesIO(msg)
        self.codec.decode(buf)

    def test_non_integer_content_length_raises(self):
        msg = self.msg.decode()\
            .replace('content-length:','content-length:aaaa')
        buf = io.BytesIO(msg.encode())
        self.assertRaises(FatalException, self.codec.decode, buf)

        buf.seek(0)
        self.assertRaises(MalformedFrame, self.codec.decode, buf)
