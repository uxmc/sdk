# encoding: utf-8
from __future__ import with_statement
from __future__ import absolute_import
import threading
import time

import logging

from sd.communication.server.protocol import function_code
from sd.communication.server.protocol.protocol import ProtocolMessage
from sd import utils

__author__ = u'Yonka'


class RequestInfo(object):
    DEFAULT_TIME_OUT = 1000

    def __init__(
            self,
            protocol_message=None,
    ):
        self.timeout = self.DEFAULT_TIME_OUT
        self.createTime = int(time.time() * 1000)
        if protocol_message is None:
            protocol_message = ProtocolMessage()
        self.protocolMessage = protocol_message
        self._cond = threading.Event()
        self._cond.clear()

    # 注意： 这种场景下，并不在 __dict__ 中，序列化时要注意... = =
    @property
    def reqId(self):
        return self.protocolMessage.reqId

    @reqId.setter
    def reqId(self, req_id):
        # if self.protocolMessage is not None:
        self.protocolMessage.reqId = req_id

    @property
    def fc(self):
        return self.protocolMessage.fc

    @fc.setter
    def fc(self, fc):
        self.protocolMessage.fc = fc

    @property
    def dataType(self):
        return self.protocolMessage.dataType

    @dataType.setter
    def dataType(self, data_type):
        self.protocolMessage.dataType = data_type

    @property
    def data(self):
        return self.protocolMessage.body

    @data.setter
    def data(self, data):
        self.protocolMessage.body = data

    def is_timeout(self):
        return self.timeout > 0 and (self.timeout + self.createTime) < utils.timestamp()

    def wait(self):
        if self._cond.is_set():
            logging.warn("set before wait for requestId %d", self.protocolMessage.reqId)
        self._cond.wait()

    def notify_all(self):
        self._cond.set()

    def __str__(self):
        return u"RequestInfo(protocol_message: %s)" % self.protocolMessage


class ResponseInfo(RequestInfo):
    FAIL_REASON_TIMEOUT = 1
    FAIL_REASON_CLEANUP_4_DISCONNECT = 2

    def __init__(
            self,
            # success: bool = False,
            # timed_out: bool = False,
            protocol_message=None
    ):
        super(ResponseInfo, self).__init__(protocol_message)
        self.success = False
        self.failReason = 0

    def is_success(self):
        return self.protocolMessage.fc != function_code.RESP_ST_ERROR
