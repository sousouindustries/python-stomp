

STOMP_VERSION = '1.2'
ACCEPT_VERSIONS = '1.0,1.1,1.2'

CONNECT     = 'CONNECT'
STOMP       = 'STOMP'
CONNECTED   = 'CONNECTED'
SEND        = 'SEND'
SUBSCRIBE   = 'SUBSCRIBE'
UNSUBSCRIBE = 'UNSUBSCRIBE'
ACK         = 'ACK'
NACK        = 'NACK'
BEGIN       = 'BEGIN'
COMMIT      = 'COMMIT'
ABORT       = 'ABORT'
DISCONNECT  = 'DISCONNECT'
MESSAGE     = 'MESSAGE'
RECEIPT     = 'RECEIPT'
ERROR       = 'ERROR'
NULL        = chr(0)
LF          = chr(10)
CR          = chr(13)
ESC         = chr(92)
COL         = chr(58)
BS          = chr(92)

ACK_AUTO        = 'auto'
ACK_CLIENT      = 'client'
ACK_INDIVIDUAL  = 'client-individual'

FRAME_TYPES = [
    CONNECT,
    STOMP,
    CONNECTED,
    SEND,
    SUBSCRIBE,
    UNSUBSCRIBE,
    ACK,
    NACK,
    BEGIN,
    COMMIT,
    ABORT,
    DISCONNECT,
    MESSAGE,
    RECEIPT,
    ERROR
]


HDR_ACK = 'ack'
HDR_CONTENT_LENGTH = 'content-length'
HDR_CONTENT_TYPE = 'content-type'
HDR_DESTINATION = 'destination'
HDR_HEARBEAT = 'heart-beat'
HDR_ID = 'id'
HDR_MESSAGE_ID = 'message-id'
HDR_RECEIPT = 'receipt'
HDR_RECEIPT_ID = 'receipt-id'
HDR_SUBSCRIPTION = 'subscription'
HDR_VERSION = 'version'
