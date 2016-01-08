import unittest

from stomp.transport.message import Message
from stomp.frames import Frame
from stomp.const import MESSAGE
from stomp.const import HDR_CONTENT_LENGTH
from stomp.const import HDR_DESTINATION
from stomp.const import HDR_MESSAGE_ID
from stomp.const import HDR_SUBSCRIPTION
from stomp.exc import StompException


class MessageTestCase(unittest.TestCase):

    def test_invalid_content_length_raises(self):
        headers = [
            (HDR_DESTINATION, '/queue/foo'),
            (HDR_MESSAGE_ID, 'foo'),
            (HDR_SUBSCRIPTION, 'bar'),
            (HDR_CONTENT_LENGTH, 'baz')
        ]
        frame = Frame(MESSAGE, headers, "Hello world!")
        self.assertRaises(StompException, Message.fromframe, None, None, frame)


if __name__ == '__main__':
    unittest.main()
