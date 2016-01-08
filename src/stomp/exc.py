

class FatalException(Exception):
    pass


class InvalidCommandType(FatalException):
    pass


class MalformedFrame(FatalException):
    pass


class StompException(FatalException):

    @classmethod
    def fromframe(cls, frame):
        return cls(frame)


class FrameNotConfirmed(Exception):
    pass
