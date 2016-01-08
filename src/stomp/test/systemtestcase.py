import unittest

from stomp.transport.connection import Connection
from stomp.transport.receiptmanager import ReceiptManager
from stomp.test.utils import get_test_settings


class SystemTestCase(unittest.TestCase):

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
                "Configure the STOMP test enviroment ({0})".format(settings))

    def setUp(self):
        self.connection = Connection(self.settings)
        self.receipts = ReceiptManager(self.connection)
