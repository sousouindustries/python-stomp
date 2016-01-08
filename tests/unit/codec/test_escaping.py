import functools
import unittest

from stomp.codec import Codec
from stomp.const import CONNECT
from stomp.const import CONNECTED
from stomp.const import ESC
from stomp.const import SEND


class EscapingTestCase(unittest.TestCase):
    # - \r (octet 92 and 114) translates to carriage return (octet 13)
    # - \n (octet 92 and 110) translates to line feed (octet 10)
    # - \c (octet 92 and 99) translates to : (octet 58)
    # - \\ (octet 92 and 92) translates to \ (octet 92)

    def setUp(self):
        self.escape = functools.partial(Codec()._escape, SEND)
        self.escape_base = Codec()._escape
        self.raw = 'header'

    def test_escape_line_feed(self):
        value = self.escape(self.raw + chr(10))
        self.assertEqual(value, self.raw + ESC + chr(110))

    def test_escape_carriage_return(self):
        value = self.escape(self.raw + chr(13))
        self.assertEqual(value, self.raw + ESC + chr(114))

    def test_escape_colon(self):
        value = self.escape(self.raw + chr(58))
        self.assertEqual(value, self.raw + ESC + chr(99))

    def test_escape_backslash(self):
        value = self.escape(self.raw + chr(92))
        self.assertEqual(value, self.raw + ESC + ESC)

    def test_escape_line_feed_connect(self):
        value = self.escape_base(CONNECT, self.raw + chr(10))
        self.assertEqual(value, self.raw + chr(10))

    def test_escape_carriage_return_connect(self):
        value = self.escape_base(CONNECT, self.raw + chr(13))
        self.assertEqual(value, self.raw + chr(13))

    def test_escape_colon_connect(self):
        value = self.escape_base(CONNECT, self.raw + chr(58))
        self.assertEqual(value, self.raw + chr(58))

    def test_escape_line_feed_connected(self):
        value = self.escape_base(CONNECTED, self.raw + chr(10))
        self.assertEqual(value, self.raw + chr(10))

    def test_escape_carriage_return_connected(self):
        value = self.escape_base(CONNECTED, self.raw + chr(13))
        self.assertEqual(value, self.raw + chr(13))

    def test_escape_colon_connected(self):
        value = self.escape_base(CONNECTED, self.raw + chr(58))
        self.assertEqual(value, self.raw + chr(58))
