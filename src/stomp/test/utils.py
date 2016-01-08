from stomp.conf import settings_factory

from stomp.test.const import TEST_HOST
from stomp.test.const import TEST_VHOST
from stomp.test.const import TEST_PORT
from stomp.test.const import TEST_USER
from stomp.test.const import TEST_PASSWORD


def get_test_settings(**params):
    params.setdefault('host', TEST_HOST)
    params.setdefault('port', TEST_PORT)
    params.setdefault('vhost', TEST_VHOST)
    params.setdefault('username', TEST_USER)
    params.setdefault('password', TEST_PASSWORD)
    return settings_factory(**params)
