import unittest
import uuid

from stomp import test
from stomp.exc import FrameNotConfirmed
from stomp.frames import SendFrame


class SendTestCase(test.SystemTestCase):

    def setUp(self):
        super(SendTestCase, self).setUp()
        self.connection.connect()
        self.body = "Hello world!"

    def tearDown(self):
        super(SendTestCase, self).tearDown()
        self.connection.close()

    def test_send(self):
        frame = SendFrame([('destination', '/queue/test.python.send')],
            body=self.body)
        self.connection.send_frame(frame)

    def test_send_with_receipt(self):
        receipt_id = uuid.uuid4().hex
        headers = [
            ('receipt', receipt_id),
            ('destination', '/queue/test.python.send')
        ]
        frame = SendFrame(headers, body=self.body)
        self.connection.send_frame(frame)

    def test_receipt_not_received_raises(self):
        receipt_id = uuid.uuid4().hex
        headers = [
            ('receipt', receipt_id),
            ('destination', '/queue/test.python.send')
        ]
        frame = SendFrame(headers, body=self.body)
        self.connection.send = lambda *a, **k: 0
        self.connection._max_retries = 1
        self.connection._receipt_timeout = 100
        self.assertRaises(FrameNotConfirmed,
            self.connection.send_frame, frame)


if __name__ == '__main__':
    unittest.main()
