from stomp import test

from stomp.const import ACK_AUTO
from stomp.const import ACK_CLIENT


class SubscriptionTestCase(test.TransportTestCase):
    destinations = [
        '/queue/SubscriptionTestCase',
        '/topic/SubscriptionTestCase'
    ]

    def send_message(self, *args, **kwargs):
        return self.transport.send(*args, **kwargs)

    def test_subscribe(self):
        self.transport.session.subscribe('/queue/SubscriptionTestCase')

    def test_subscribe_multiple(self):
        self.transport.session.subscribe(self.destinations)

    def test_set_ack_mode(self):
        self.transport.session.subscribe(
            self.destinations, ack_mode=ACK_AUTO)

    def test_send_message_is_received(self):
        # Subscribe to two destinations. Send a message to one destination.
        # We must receive exactly one message.
        sub = self.transport.session.subscribe(self.destinations)
        self.assertEqual(sub.message_count, 0)

        self.send_message(self.destinations[0],
            "text/plain","Hello world!",
            headers=dict(foo='bar'), receipt=True)

        self.assertEqual(sub.message_count, 1)

    def test_send_message_is_received_multiple(self):
        # Subscribe to two destinations. Send a message to multiple destinations
        # on the same subscription. We must receive exactly one message.
        sub = self.transport.session.subscribe(self.destinations)
        self.assertEqual(sub.message_count, 0)

        self.send_message(self.destinations,
            "text/plain","Hello world!", receipt=True)

        self.assertEqual(sub.message_count, 1)
        self.assertEqual(sub.frame_count, 2)
        self.assertEqual(list(sub.messages)[-1].body, b"Hello world!")


if __name__ == '__main__':
    import unittest
    unittest.main()
