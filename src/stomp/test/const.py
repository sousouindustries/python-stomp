import os


TEST_HOST = os.getenv('STOMP_TEST_HOST')
TEST_VHOST = os.getenv('STOMP_TEST_VHOST')
TEST_PORT = int(os.getenv('STOMP_TEST_PORT') or 0)
TEST_USER = os.getenv('STOMP_TEST_USER')
TEST_PASSWORD = os.getenv('STOMP_TEST_PASSWORD')
