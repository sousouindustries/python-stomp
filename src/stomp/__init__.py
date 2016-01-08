

def transport_factory(**params):
    from stomp.conf import settings_factory
    from stomp.transport.transport import Transport
    settings = settings_factory(**params)
    return Transport(settings)
