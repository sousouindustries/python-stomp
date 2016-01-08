import time

from stomp import test


class HeartBeatTestCase(test.SystemTestCase):

    def test_configure_heartbeat(self):
        c = self.create_connection(send_hb=2000, recv_hb=2000)
        c.connect()
