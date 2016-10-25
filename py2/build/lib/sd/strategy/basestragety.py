# encoding: utf-8
from __future__ import with_statement
from __future__ import absolute_import
import os
import threading
import time

import logging

from concurrent.futures import ThreadPoolExecutor

from sd.communication.server.protocol import function_code
from sd.exception.exception import RequestTimeoutException, InvalidLoginStatus, \
    RequestCleanupAsDisconnect
from sd.strategy.bean import protoquote
from sd.strategy.bean.bean import StrategyOrderDetail, StrategyError, StrategyAccountDetail, \
    StrategyOrder, StrategyConnectionInfo, StrategyPosition
from sd.strategy.bean.databean import KlineBean, TickBean
from sd.strategy.client.client import StrategyClient
from sd.strategy.historydata import HistoryData
from sd.strategy.interface import AbstractStrategy, AbstractNotifyMessageHandler, HistoryDataInterface
from sd.strategy.client.interface import AbstractAsyncMessageHandler
from sd.strategy.request import RequestInfo, ResponseInfo
from sd.utils import bean as utils_bean
from sd.communication.server.protocol.function_constants import *

__author__ = u'yonka'


class BaseStrategy(AbstractStrategy, AbstractNotifyMessageHandler, AbstractAsyncMessageHandler, HistoryDataInterface):
    DEFAULT_REQUEST_TIMEOUT = 20000
    MAX_RECONNECT_COUNT = 10

    def __init__(self, servers, user_name, pass_word, strategy=None, usage_type=AgentType_STRATEGY_QUOTE,
                 description=None, mode=1, start_time=None, end_time=None, base_money=None, symbol='',
                 commission_ratio=None, adjust_price_type=0, history_data_server=HISTORY_QUOTE_SERVER):
        self.servers = servers.split(";")
        self.server_index = 0
        host = self.servers[self.server_index].split(":")[0]
        port = int(self.servers[self.server_index].split(":")[1])
        self.connClient = StrategyClient(
            host,
            port,
            message_handler=self
        )
        self.requestId = int(time.time() * 1000)
        self.externalAsyncMessageHandler = None
        self.externalNotifyMessageHandler = self
        self.connectionInfo = StrategyConnectionInfo(account_id=user_name, strategy_id=strategy,
                                                     password=pass_word, description=description, mode=mode,
                                                     base_money=base_money, commission_ratio=commission_ratio,
                                                     adjust_price_type=adjust_price_type, symbol=symbol,
                                                     start_time=start_time, end_time=end_time)
        self.strategyConnectionInfo = self.connectionInfo
        self.autoReconnect = True
        self.login = False
        self.agentType = usage_type
        self.reconnectLock = threading.Lock()
        self.requestIdLock = threading.Lock()
        self.finish = False
        self.reconnect_time = 0
        self.reConnectWorker = None
        self.notified_connection_error = False
        self.reconnect_wait_time = 1
        self.subscribe_commands = {}
        self._base_handlers = {
            function_code.NOTIFY_ST_SUBSCRIBE: self.notify_st_subscribe_handler,
            function_code.NOTIFY_ST_ORDERDETAIL: self.notify_st_order_detail_handler,
            function_code.COMMAND_ST_EXIT: self.command_strategy_exit_handler
        }
        self.history_data_func_impl = HistoryData(user_name, pass_word, history_data_server)

    def set_external_notify_message_handler(self, external_notify_message_handler):
        self.externalNotifyMessageHandler = external_notify_message_handler

    def _reconnect(self):
        while True:
            try:
                if self.connClient is not None and self.connClient.is_open():
                    time.sleep(self.reconnect_wait_time)
                    continue
                self.reconnect_time += 1
                if self.reconnect_time > BaseStrategy.MAX_RECONNECT_COUNT:
                    self.externalNotifyMessageHandler.on_notify_connection_error(
                        "reconnect failed, disconnect from server , please check your network")
                    break
                # else:
                #     self.notified_connection_error = True
                #     self.reconnect_wait_time *= 2
                #     if self.reconnect_wait_time > 129:
                #         self.reconnect_wait_time = 128
                self.login = False
                if self.connClient is not None:
                    self.connClient.close()
                    self.connClient = None
                self.server_index = (self.server_index + 1) % (len(self.servers))
                host = self.servers[self.server_index].split(":")[0]
                port = int(self.servers[self.server_index].split(":")[1])
                self.connClient = StrategyClient(
                    host,
                    port,
                    message_handler=self
                )

                logging.warn("begin %d reconnect with host:%s,port:%d", self.reconnect_time, host, port)
                if self.init().errorId != 0:
                    logging.warn("%d reconnect with host:%s,port:%d failed", self.reconnect_time, host,
                                 port)
                    self.login = False
                    if self.connClient is not None:
                        self.connClient.close()
                        self.connClient = None
                else:
                    logging.info("reconnect success at %d try, begin to auto subscribe " % self.reconnect_time)
                    for key in self.subscribe_commands:
                        (data_type, symbol) = key.split("_")
                        self.req_subscribe(int(data_type), symbol)
                    self.reconnect_time = 0
                    self.reconnect_wait_time = 1
                time.sleep(self.reconnect_wait_time)
            except Exception as e:
                logging.exception(e)

    def init(self):
        logging.debug("connect to %s:%d for %s", self.connClient.host, self.connClient.port,
                      "trader" if (AgentType_STRATEGY_TRADE == self.agentType) else "quote")
        err = self._new_succeed_error()
        if self.connClient.connect():
            err = self.req_login()
            if err.errorId == 0:
                self.login = True
                if self.reConnectWorker is None:
                    self.reConnectWorker = ThreadPoolExecutor(1)
                    self.reConnectWorker.submit(self._reconnect)
            else:
                logging.warning(u"self.default_req_login() failed")
        else:
            err = StrategyError(100, "connect error")
            logging.warning(u"self.connClient.connect() failed")
        return err

    def finish(self):
        self.finish = True

    def run(self, timeout=None):
        runtime = 0
        while (not self.finish):
            time.sleep(10)
            runtime += 10
            if (timeout is not None):
                if runtime >= timeout:
                    break

    def _get_and_inc_req_id(self):
        with self.requestIdLock:
            self.requestId += 1
            return self.requestId

    '''请求发生前先确认是否在登录状态，如果不是，最多等待BaseStrategy.DEFAULT_REQUEST_TIMEOUT 时间'''

    def get_bars(self, symbol="SHSE.rb1610", begin_time="2016-08-19 21:00:00", end_time="2016-08-20 21:00:00",
                 bar_type=60, time_out=None):
        return self.history_data_func_impl.get_bars(symbol, begin_time, end_time, bar_type, time_out)

    def get_last_n_ticks(self, symbol, n, time_out=None):
        return self.history_data_func_impl.get_last_n_ticks(symbol, n, time_out)

    def get_last_n_bars(self, symbol="SHSE.rb1610", bar_type=60, n=5, time_out=None):
        return self.history_data_func_impl.get_last_n_bars(symbol, bar_type, n, time_out)

    def get_ticks(self, symbol="SHSE.rb1610", begin_time="2016-08-19 21:00:00", end_time="2016-08-20 21:00:00",
                  time_out=None):
        return self.history_data_func_impl.get_ticks(symbol, begin_time, end_time, time_out)

    def get_last_n_daily_bars(self, symbol="SHSE.rb1610", n=10, time_out=None):
        return self.history_data_func_impl.get_last_n_daily_bars(symbol, n, time_out)

    def get_daily_bars(self, symbol="SHSE.rb1610", begin_time="2016-08-19", end_time="2016-08-20", time_out=None):
        return self.history_data_func_impl.get_daily_bars(symbol, begin_time, end_time)

    def get_last_ticks(self, symbol=None, time_out=None):
        return self.history_data_func_impl.get_last_ticks(symbol, time_out)

    def _check_login_status(self):

        if self.login:
            return
        wait_time = 0

        while wait_time * 1000 < BaseStrategy.DEFAULT_REQUEST_TIMEOUT:
            if self.login:
                return self.login
            else:
                wait_time += 1
                time.sleep(1)
        raise InvalidLoginStatus("operation before login, connection is broken")

    def _build_request_info(self, timeout, fc):
        request_info = RequestInfo()
        request_info.fc = fc
        request_info.dataType = self.agentType
        request_info.timeout = timeout
        request_info.reqId = self._get_and_inc_req_id()
        return request_info

    @classmethod
    def _convert_2_strategy_error(cls, message):
        return StrategyError().from_json(message.body)

    @classmethod
    def _new_500_error(cls):
        return StrategyError(error_id=500, error_msg=u"internal system error for request")

    @classmethod
    def _new_connection_error(cls):
        return StrategyError(error_id=400, error_msg=u"connection error for request")

    @classmethod
    def _new_succeed_error(cls):
        return StrategyError(error_id=0, error_msg=u"ok")

    def _handle_request_exception(self, e, safe=True):
        if 1:
            if isinstance(e, RequestTimeoutException):
                return StrategyError(302, "timeout for request")
            elif isinstance(e, InvalidLoginStatus):
                return StrategyError(300, "operation before login status, maybe connection is broke")
            elif isinstance(e, RequestCleanupAsDisconnect):
                return StrategyError(301, "request failed as disconnect")
            else:
                return BaseStrategy._new_500_error()

    def req_subscribe(self, data_type=None, symbol=None):
        s = "%d.%s" % (data_type, symbol)
        logging.info("req_subscribe:" + s)
        try:
            self._check_login_status()
            request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.REQ_ST_SUBSCRIBE)
            request_info.data = s
            response_info = self.connClient.sync_rpc(request_info)
            rt = self._convert_2_strategy_error(response_info.protocolMessage)
            if rt.errorId == 0:
                self.subscribe_commands["%d_%s" % (data_type, symbol)] = True

            return rt
        except Exception as e:
            logging.exception("%s", e)
            return self._handle_request_exception(e)

    def req_order_list(self, strategy_id):
        result = None
        err = self._new_succeed_error()
        try:
            self._check_login_status()
            request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.REQ_ST_ORDERLIST)
            request_info.data = strategy_id
            response_info = self.connClient.sync_rpc(request_info)
            data = response_info.data
            if response_info.is_success():
                result = utils_bean.json_load_bean_list(data, StrategyOrderDetail)
            else:
                err = StrategyError().from_json(data)
        except Exception as e:
            logging.exception("%s", e)
            err = self._handle_request_exception(e)
        return result, err

    def req_account_detail(self, trading_day=None):
        result = None
        err = self._new_succeed_error()
        try:
            self._check_login_status()
            request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.REQ_ST_ACCOUNTETAIL)
            request_info.data = trading_day
            response_info = self.connClient.sync_rpc(request_info)
            data = response_info.data
            if response_info.is_success():
                result = utils_bean.json_load_bean_list(data, StrategyAccountDetail)
            else:
                err = StrategyError().from_json(data)
        except Exception as e:
            logging.exception("%s", e)
            err = self._handle_request_exception(e)
        return result, err

    def req_position(self, strategy_id=None):
        result = None
        err = self._new_succeed_error()
        try:
            self._check_login_status()
            request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.REQ_ST_POTITIONDSTATICS)
            request_info.data = strategy_id
            response_info = self.connClient.sync_rpc(request_info)
            data = response_info.data
            if response_info.is_success():
                result = utils_bean.json_load_bean_list(data, StrategyPosition)
            else:
                err = StrategyError().from_json(data)
        except Exception as e:
            logging.exception("%s", e)
            err = self._handle_request_exception(e)
        return result, err

    def req_cancel_order(self, cancel_order_id):
        err = self._new_succeed_error()
        try:
            self._check_login_status()
            request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.REQ_ST_CANCELORDER)
            request_info.data = str(cancel_order_id)
            response_info = self.connClient.sync_rpc(request_info)
            err = self._convert_2_strategy_error(response_info.protocolMessage)
        except Exception as e:
            logging.exception("%s", e)
            err = self._handle_request_exception(e)
        return err

    def send_order(self, symbol=None, bs_flag=None, position_effect=None, price_type=None, price=None, volume=None,
                   strategy=None, order_time=None, hedge_type=HEDGE_FLAG_HEDGE):
        if strategy is None:
            strategy = self.strategyConnectionInfo.strategyName

        order_info = StrategyOrder(userName=self.connectionInfo.userName, price=price, priceType=price_type,
                                   instrument=symbol, bsFlag=bs_flag,
                                   positionEffect=position_effect,
                                   strategyName=strategy, volume=volume, hedgeFlag=hedge_type, orderTime=order_time)
        result = None
        err = self._new_succeed_error()
        logging.info("Requested order info:%s", order_info.to_json())
        try:
            self._check_login_status()
            request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.REQ_ST_ORDER)
            order_info.strategyClientID = os.getpid()  # XXX 是不是这个？
            request_info.data = order_info.to_json()
            response_info = self.connClient.sync_rpc(request_info)
            data = response_info.data
            if response_info.is_success():
                result = data
                logging.info("response order: %s", data)
                result = long(result)
            else:
                err = StrategyError().from_json(data)
        except Exception as e:
            logging.exception(e)
            err = self._handle_request_exception(e)
        return result, err

    def req_un_subscribe(self, data_type, symbol):
        try:
            self._check_login_status()
            request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.REQ_ST_UNSUBSCRIBE)
            request_info.data = symbol
            response_info = self.connClient.sync_rpc(request_info)
            rt = self._convert_2_strategy_error(response_info.protocolMessage)
            if rt.errorId == 0:
                key = "%d_%s" % (data_type, symbol)
                if self.subscribe_commands.has_key(key):
                    del self.subscribe_commands[key]
        except Exception as e:
            logging.exception("%s", e)
            return self._handle_request_exception(e)

    def req_login(self):
        if self.login:
            return StrategyError(0, "success")
        try:
            request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.STRATEGYLOGIN)
            data = self.connectionInfo.to_json()
            request_info.data = data
            response_info = self.connClient.sync_rpc(request_info)
            err = self._convert_2_strategy_error(response_info.protocolMessage)
            if err.errorId == 0:
                # 返回的sessionid保存下来给重连使用。
                self.connectionInfo.sessionId = err.errorMsg
                logging.info(u"请求连接成功，err is %s", err.to_json())
                err.errorMsg = "success"
            else:
                logging.exception(u"请求连接失败，err is %s", err.to_json())
            return err
        except Exception as e:
            logging.exception("%s", e)
            return self._new_500_error()

    def on_notify_order_detail(self, order_detail):
        pass

    def on_notify_quote(self, data_tye, data):
        pass

    def on_notify_connection_error(self, reason=""):
        logging.error("Connection error:" + reason)

    def on_command_strategy_exit(self, reason=None):
        logging.error("Received command to exit the strategy from server")

    def notify_st_subscribe_handler(self, async_message):
        try:
            response_info = ResponseInfo(protocol_message=async_message)
            data = None
            if response_info.dataType == TICK:
                data = utils_bean.proto_to_bean(response_info.protocolMessage.body, protoquote.TickBean,
                                                TickBean)
            elif response_info.dataType == BAR:
                data = utils_bean.proto_to_bean(response_info.protocolMessage.body, protoquote.KLineBean,
                                                KlineBean)
            elif response_info.dataType == DAILY_BAR:
                data = utils_bean.proto_to_bean(response_info.protocolMessage.body, protoquote.KLineBean,
                                                KlineBean)
            if data:
                self.externalNotifyMessageHandler.on_notify_quote(response_info.dataType, data)
        except Exception, e:
            logging.exception(u"%s", e)

    def handle_async_message(self, async_message):
        def _base_handle_async_message(self, async_message):
            handler = self._base_handlers.get(async_message.fc)
            if handler is not None:
                handler(async_message)

        if self.externalAsyncMessageHandler is not None:
            self.externalAsyncMessageHandler.handle_async_message(self, async_message)
        else:
            _base_handle_async_message(self, async_message)

    def notify_st_order_detail_handler(self, async_message):
        try:
            logging.debug(u"return orderdetail: %s", async_message.body)
            strategy_order_detail = StrategyOrderDetail().from_json(async_message.body)
            self.externalNotifyMessageHandler.on_notify_order_detail(strategy_order_detail)
        except Exception, e:
            logging.exception(e)

    def command_strategy_exit_handler(self, async_message):
        try:
            logging.warn(u"received command  strategy exit")
            self.externalNotifyMessageHandler.on_command_strategy_exit(async_message.body)
        except Exception, e:
            logging.exception(e)
        os._exit(1)
