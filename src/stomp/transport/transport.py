from stomp.transport.connection import Connection


class Transport(object):
    """Represents the transport between the server and the client and
    exposes all methods of the ``STOMP`` protocol.
    """

    @property
    def messages(self):
        for sub in self.session.subscriptions:
            for msg in sub:
                yield msg

    def __init__(self, settings):
        self.settings = settings
        self.connection = Connection(settings)
        self.session = None

    def start(self):
        """Connects to the ``STOMP`` server and starts the transport."""
        self.session = self.connection.connect()

    def stop(self):
        """Stop the transport and disconnect from the server."""
        self.connection.close()

    def subscribe(self, destinations, **opts):
        """Subscribes to the specified destinations.

        Args:
            destinations: a string specifying a single
                destination; or a list holding multiple
                destinations.
            ack_mode: specifies the acknowledgement mode
                for incoming frames. Must be one of ``auto``,
                ``client`` or ``client-individual``.

        Returns:
            None
        """
        return self.session.subscribe(destinations, **opts)

    def unsubscribe_all(self):
        """Send an ``UNSUBSRCIBE`` frame for all subscriptions."""
        for sub in self.session:
            sub.destroy()

    def send(self, destinations, content_type, body, headers=None,
        receipt=False):
        from stomp.frames import SendFrame
        headers = list((headers or {}).items())
        headers.extend([
            ('content-type', content_type),
            ('destination', self.connection.join_destination(destinations))
        ])
        frame = SendFrame(headers, body, with_receipt=receipt)
        self.connection.send_frame(frame)
