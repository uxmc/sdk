# encoding: utf-8

__author__ = u'Yonka'


class ConnectionBrokenException(RuntimeError):
    pass


class AuthFailedException(RuntimeError):
    pass


class ReconnectionMoreThanMaxTry(RuntimeError):
    pass


class InvalidLoginStatus(RuntimeError):
    pass


class RequestTimeoutException(RuntimeError):
    pass


class InvalidRequestRuntimeException(RuntimeError):
    pass


class RequestCleanupAsDisconnect(RuntimeError):
    pass
