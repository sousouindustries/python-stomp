import threading

from stomp.const import RECEIPT
from stomp.const import SEND
from stomp.exc import FrameNotConfirmed


class ReceiptManager(object):

    def __init__(self, connection):
        self.connection = connection
        connection.register_observer(self)
        self.receipts = {}
        self.lock = threading.Lock()

    def wait(self, receipt_id, timeout=None):
        """Block until a ``RECEIPT`` frame with the given ``receipt_id`` is
        received or `timeout` is reached.
        """
        if timeout is not None:
            timeout = int(timeout / 1000)
        if not self.receipts[receipt_id].wait(timeout):
            raise FrameNotConfirmed

        return True

    def notify(self, event, frame, **params):
        """Notify the :class:`ReceiptManager` manager that a certain
        event has occurred.
        """
        if event not in (self.connection.EVNT_FRAME_RECV, self.connection.EVNT_FRAME_SENT):
            return

        if (frame.command == RECEIPT) and event == self.connection.EVNT_FRAME_RECV:
            # If the receipt is in our registry, fire the event indicating
            # listeners that the receipt has been received.
            receipt_id = frame.headers.get('receipt-id')
            with self.lock:
                event = self.receipts.pop(receipt_id)
                event.set()
            raise self.connection.DiscardFrame

        # On SEND frames, if a receipt was specified in the headers,
        # create an event for it so that listeners can block until
        # the confirmation from the STOMP server arrives.
        if (frame.expects_receipt())\
        and (event == self.connection.EVNT_FRAME_SENT):
            self.receipts[frame.receipt_id] = threading.Event()
