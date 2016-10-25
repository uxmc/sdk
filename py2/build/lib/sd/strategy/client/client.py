# encoding: utf-8
from __future__ import with_statement
from __future__ import absolute_import
import threading
import time
import unittest

import logging

from concurrent.futures import ThreadPoolExecutor

from sd.communication.client import connection
from sd.communication.server import protocol
from sd.exception.exception import ConnectionBrokenException, RequestTimeoutException, RequestCleanupAsDisconnect
from sd.strategy.client.interface import AbstractStrategyClient
from sd.strategy.request import ResponseInfo
from sd import utils

__author__ = u'Yonka'


class StrategyClient(AbstractStrategyClient):
    MAX_TRIES = 3
    RECONNECT_INTERNAL = 1
    HEART_BEAT_TIMEOUT = 10
    HEART_BEAT_INTERVAL = 5

    def __init__(
            self,
            host=None,
            port=None,
            read_timeout=0,
            conn_timeout=0,
            message_handler=None
    ):
        self.host = host
        self.port = port
        self.readTimeout = read_timeout
        self.connTimeout = conn_timeout
        self.messageHandler = message_handler
        self.open = False
        self.closing = False

        self._lock = threading.Lock()

        self.baseConn = None
        self.ioReaderWorkers = None
        self.bussWorkers = None
        self.heartbeatMonitor = None
        self.timeoutMonitor = None

        self.requestCache = {}
        self.responseCache = {}

    def _build_base_conn(self):
        for i in xrange(self.MAX_TRIES):
            try:
                self.baseConn = connection.new_conn(self.host, self.port, self.readTimeout, self.connTimeout)
                return True
            except Exception, e:
                logging.exception(u"unable to build connection to server %s with port %d e is %s", self.host, self.port,
                                  e)
                try:
                    time.sleep(self.RECONNECT_INTERNAL)
                except Exception, e1:
                    logging.exception(u"unable to build connection to server, due to thread interrupt, e is %s", e1)
        return False

    def _write(self, protocol_message):  # throw exception if write error!! must handle exception
        u"""
        may raise ConnectionBrokenException
        """
        logging.debug("Send message:%s", protocol_message)
        if self.open:
            result = self.baseConn.write(protocol_message)
            if not result:
                self.open = False
                raise ConnectionBrokenException(u"connection broken")
        else:
            raise ConnectionBrokenException(u"connection  is broken")

    def _do_heartbeat(self):
        try:
            self._write(protocol.new_strategy_hb_msg())
        except Exception, e:
            logging.warn("send heartbeat failed as connection problem, notify connection error", e)
            self.open = False
            return False
        return self.open

    def _check_timeout(self):
        request_cache = dict(self.requestCache)  # 作为client可以
        for req_id, req in request_cache.items():
            if req is None or req_id in self.responseCache:
                continue  # req should not be None
            if req.is_timeout():
                resp = ResponseInfo()
                resp.failReason = ResponseInfo.FAIL_REASON_TIMEOUT
                self.responseCache[req_id] = resp
                req.notify_all()
        return self.open

    def _read_conn(self):
        try:
            while True:
                if not self.open:
                    # 这里如果conn被关闭也不重连的话，会一直while循环吃大量CPU
                    logging.warn("connection is not in open state ,notify connection error")
                    raise ConnectionBrokenException(u"connection  is in abnormanl state")
                protocol_msg = self.baseConn.read()  # type: ProtocolMessage
                if protocol_msg is None:
                    self.open = False
                    logging.warn("client is not open")
                    raise ConnectionBrokenException(u"connection  is in abnormanl state")
                logging.debug("Received message:%s", protocol_msg)
                if protocol_msg.is_hb_message():
                    self._write(protocol.new_strategy_hb_ack_msg())
                elif protocol_msg.is_ack_message():
                    pass
                else:
                    req = self.requestCache.pop(protocol_msg.reqId, None)  # type: RequestInfo
                    if req is None:
                        self.bussWorkers.submit(
                            lambda async_message: self.messageHandler.handle_async_message(async_message),
                            protocol_msg
                        )
                    else:
                        self.responseCache[protocol_msg.reqId] = ResponseInfo(protocol_msg)
                        req.notify_all()
        except Exception, e:
            logging.exception(u"_read_conn met exception: %s", e)
            self.open = False

    def sync_rpc(self, request_info):
        u"""
        may raise RequestTimeoutException or ConnectionBrokenException
        """
        if not self.is_open():
            raise ConnectionBrokenException(u"socket broken")
        self.requestCache[request_info.reqId] = request_info
        self._write(request_info.protocolMessage)
        request_info.wait()
        resp = self.responseCache.pop(request_info.reqId, None)  # type: ResponseInfo
        if resp is None:
            raise ConnectionBrokenException(u"socket broken")  # should not, when connection  error and close it
        if request_info.is_timeout() or resp.failReason == ResponseInfo.FAIL_REASON_TIMEOUT:
            raise RequestTimeoutException(u"request %d timed out, reqTime: %d, curTime: %d, timeout: %d, req is %s" % (
                request_info.reqId, request_info.createTime, utils.timestamp(), request_info.timeout, request_info))
        if resp.failReason == ResponseInfo.FAIL_REASON_CLEANUP_4_DISCONNECT:
            raise RequestCleanupAsDisconnect(u"request %d cleaned up as disconnect", request_info.reqId)

        return resp

    def close(self):
        try:
            self.closing = True
            self.open = False

            if self.baseConn is not None and self.baseConn.is_open():
                self.baseConn.close()
                self.baseConn = None

            if self.ioReaderWorkers is not None:
                self.ioReaderWorkers.shutdown()
            if self.timeoutMonitor is not None:
                self.timeoutMonitor.shutdown()
            if self.heartbeatMonitor is not None:
                self.heartbeatMonitor.shutdown()

            for req in self.requestCache.values():
                '''
                    如何处理假如在断开的时候还有正在进行的同步的请求？告知connection reset，交给上层去处理
                '''
                resp = ResponseInfo()
                resp.failReason = ResponseInfo.FAIL_REASON_TIMEOUT
                self.responseCache[req.reqId] = resp
                req.notify_all()
            self.requestCache = {}
            self.responseCache = {}

            self.closing = False
        except Exception, e:
            logging.exception(e)
            self.closing = False

    def connect(self):
        if not self._build_base_conn():
            logging.warn(u"Socket connection timeout")
            self.open = False
            return False
        else:
            logging.debug(u"Socket connection open")
            self.open = True

        self.ioReaderWorkers = ThreadPoolExecutor(1)
        self.bussWorkers = ThreadPoolExecutor(1)
        self.heartbeatMonitor = ThreadPoolExecutor(1)
        self.heartbeatMonitor.submit(utils.schedule_task(self._do_heartbeat, StrategyClient.HEART_BEAT_INTERVAL,
                                                         StrategyClient.HEART_BEAT_TIMEOUT, 0))

        self.timeoutMonitor = ThreadPoolExecutor(1)
        self.timeoutMonitor.submit(utils.schedule_task(self._check_timeout, 1, 1, 0))

        self.ioReaderWorkers.submit(self._read_conn)

        return True

    def is_open(self):
        return self.open and not self.closing

    def async_rpc(self, request_info):
        pass
        # if not self.is_open():
        #     raise ConnectionBrokenException(u"socket broken")
        # self._write(request_info.protocolMessage)
        # return True


class TestClient(unittest.TestCase):
    def test_client(self):
        logging.basicConfig(format=u'%(asctime)s %(message)s', datefmt=u'%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
        c = StrategyClient(u"101.200.228.73", 8080)
        # c = StrategyClient("101.200.228.73", 3333)
        # c = StrategyClient("localhost", 8080)
        c.connect()
        time.sleep(10000)
