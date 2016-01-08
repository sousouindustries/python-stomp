from stomp.frames.base import Frame
from stomp import const


ConnectFrame = Frame.factory(const.CONNECT)
DisconnectFrame = Frame.factory(const.DISCONNECT)
SendFrame = Frame.factory(const.SEND)
SubscribeFrame = Frame.factory(const.SUBSCRIBE)
UnsubscribeFrame = Frame.factory(const.UNSUBSCRIBE)
