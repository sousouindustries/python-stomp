from collections import namedtuple


Settings = namedtuple('Settings', ['host','port','vhost','username',
    'password','send_hb','recv_hb','path_separator','dest_separator',
    'queue_prefix','topic_prefix','dsub_prefix','message_factory'])


def settings_factory(**kwargs):
    kwargs.setdefault('send_hb', 0)
    kwargs.setdefault('recv_hb', 0)

    # These settings are the Apache Apollo defaults.
    kwargs.setdefault('path_separator', '.')
    kwargs.setdefault('dest_separator', ',')
    kwargs.setdefault('queue_prefix', '/queue/')
    kwargs.setdefault('topic_prefix', '/topic/')
    kwargs.setdefault('dsub_prefix', '/dsub/')
    kwargs.setdefault('message_factory', None)
    return Settings(**kwargs)
