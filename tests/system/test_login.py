import unittest

from stomp import test
from stomp.exc import StompException


class LoginTestCase(test.SystemTestCase):

    def test_login(self):
        self.connection.connect()

    def test_login_with_invalid(self):
        c = self.create_connection(username='foo', password='bar')
        self.assertRaises(StompException, c.connect)


if __name__ == '__main__':
    unittest.main()
