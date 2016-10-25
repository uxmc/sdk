# encoding: utf-8
from __future__ import with_statement
from __future__ import absolute_import
import time
import unittest

import logging

from sd.communication.server.protocol.function_constants import *
from sd.strategy.basestragety import BaseStrategy
from sd.strategy.bean.bean import StrategyError
from sd.strategy.interface import AbstractStrategy, AbstractNotifyMessageHandler, HistoryDataInterface

__author__ = u'yonka'


class SimpleStrategy(AbstractStrategy, AbstractNotifyMessageHandler, HistoryDataInterface):
    def __init__(
            self,
            trade_servers=TRADE_SERVER, quote_servers=REAL_TIME_QUOTE_SERVER, user_name=None, pass_word=None, strategy=None, description=None
    ):
        self.quoteStrategy = BaseStrategy(quote_servers, user_name, pass_word, strategy,
                                          AgentType_STRATEGY_QUOTE, None)
        self.traderStrategy = BaseStrategy(trade_servers, user_name, pass_word, strategy,
                                           AgentType_STRATEGY_TRADE, description)
        self.quoteStrategy.set_external_notify_message_handler(self)
        self.traderStrategy.set_external_notify_message_handler(self)

    def init(self):
        err = StrategyError(100, "connect error")
        for name, strategy in [(u"trader", self.traderStrategy), (u"quote", self.quoteStrategy)]:
            if strategy is not None:
                try:
                    err = strategy.init()
                    if err.errorId == 0:
                        logging.info(u"%s connection login succeed", name)
                    else:
                        logging.exception(u"%s connection failed.....", name)
                        return err
                except Exception, e:
                    logging.exception(u"login failed, e is %s", e)
                    return StrategyError(100, "connect error")
        return err

    def req_account_detail(self, trading_day=None):
        return self.traderStrategy.req_account_detail(trading_day)

    def get_bars(self, symbol="SHSE.rb1610", begin_time="2016-08-19 21:00:00", end_time="2016-08-20 21:00:00",
                 bar_type=60, time_out=None):
        return self.quoteStrategy.get_bars(symbol, begin_time, end_time, bar_type, time_out)

    def get_last_n_ticks(self, symbol, n, time_out=None):
        return self.quoteStrategy.get_last_n_ticks(symbol, n, time_out)

    def get_last_n_bars(self, symbol="SHSE.rb1610", bar_type=60, n=5, time_out=None):
        return self.quoteStrategy.get_last_n_bars(symbol, bar_type, n, time_out)

    def get_ticks(self, symbol="SHSE.rb1610", begin_time="2016-08-19 21:00:00", end_time="2016-08-20 21:00:00",
                  time_out=None):
        return self.quoteStrategy.get_ticks(symbol, begin_time, end_time, time_out)

    def get_last_n_daily_bars(self, symbol="SHSE.rb1610", n=10, time_out=None):
        return self.quoteStrategy.get_last_n_daily_bars(symbol, n, time_out)

    def get_daily_bars(self, symbol="SHSE.rb1610", begin_time="2016-08-19", end_time="2016-08-20", time_out=None):
        return self.quoteStrategy.get_daily_bars(symbol, begin_time, end_time)

    def get_last_ticks(self, symbol_list=None, time_out=None):
        return self.get_last_ticks(symbol_list, time_out)

    def req_order_list(self, strategy_id=None):
        return self.traderStrategy.req_order_list(strategy_id)

    def send_order(self, symbol=None, bs_flag=None, position_effect=None, price_type=None, price=None, volume=None,
                   strategy=None,
                   hedge_type=HEDGE_FLAG_HEDGE,order_time=None):
        return self.traderStrategy.send_order(symbol, bs_flag, position_effect, price_type, price, volume, strategy,
                                              order_time,hedge_type)

    def req_login(self):
        pass

    def req_subscribe(self, data_type=None, symbol=None):
        return self.quoteStrategy.req_subscribe(data_type, symbol)

    def req_position(self, strategy_id=None):
        return self.traderStrategy.req_position(strategy_id)

    def req_cancel_order(self, cancel_order_info):
        return self.traderStrategy.req_cancel_order(cancel_order_info)

    def req_un_subscribe(self, data_type, symbol):
        return self.quoteStrategy.req_un_subscribe(data_type, symbol)

    def on_notify_order_detail(self, order_detail):
        logging.info("order detail: %s", order_detail)

    def on_notify_quote(self, dataType, data):
        pass

    def on_notify_connection_error(self, reason=""):
        pass

    def on_command_strategy_exit(self, reason=""):
        pass

    def run(self, timeout=None):
        self.quoteStrategy.run(timeout)

