import unittest

from stomp.transport import Transport
from stomp.test.utils import get_test_settings


class TransportTestCase(unittest.TestCase):

    def create_connection(self, **params):
        settings = get_test_settings(**params)
        connection = Connection(settings)
        ReceiptManager(connection)
        return connection

    @classmethod
    def setUpClass(cls):
        cls.settings = settings = get_test_settings()
        if not all([settings.host, settings.port, settings.vhost,
        settings.username, settings.password]):
            raise unittest.SkipTest(
                "Configure the STOMP test environment ({0})".format(settings))

    def setUp(self):
        self.transport = Transport(self.settings)
        self.transport.start()

    def tearDown(self):
        self.transport.stop()
