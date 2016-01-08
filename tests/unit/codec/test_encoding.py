import unittest

from stomp.const import CONNECT
from stomp.const import CR
from stomp.const import LF
from stomp.const import NULL
from stomp.const import SEND
from stomp.codec import Codec
from stomp.exc import InvalidCommandType


class EncodingTestCase(unittest.TestCase):

    def setUp(self):
        self.codec = Codec()
        self.cmd = CONNECT

    def test_encode_header(self):
        raw = tuple(['key','value'])
        encoded = self.codec.encode_header(self.cmd, *raw)
        self.assertEqual(tuple(encoded.decode().split(':')), raw)

    def test_invalid_command_raises(self):
        self.assertRaises(InvalidCommandType,
            self.codec.encode, 'foo', [])

    def test_encode_with_body(self):
        body = "Hello world!"
        encoded = self.codec.encode(SEND, [], body=body)
        self.assertTrue((LF + LF + body + NULL) in encoded.decode())

    def test_encode_with_carriage_return(self):
        codec = Codec(eol=CR)
        body = "Hello world!"
        raw = codec.encode(SEND, [], body=body)

    def test_encode_with_string_input(self):
        codec = Codec()
        body = "Hello world!"
        raw = codec.encode(SEND, [], body=body)
