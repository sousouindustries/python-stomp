from stomp import test


class CloseConnectionTestCase(test.SystemTestCase):

    def test_close(self):
        c = self.create_connection()
        c.connect()
        c.close()
