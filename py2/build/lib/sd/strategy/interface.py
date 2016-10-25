from __future__ import absolute_import
from abc import ABCMeta, abstractmethod
import unittest

__author__ = u'Yonka'


class HistoryDataInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_ticks(self, symbol="SHSE.rb1610", begin_time="2016-08-19 21:00:00", end_time="2016-08-20 21:00:00",
                  time_out=None):
        pass

    @abstractmethod
    def get_last_ticks(self, symbol_list=None, time_out=None):
        pass

    @abstractmethod
    def get_last_n_ticks(self, symbol, n, time_out=None):
        pass

    @abstractmethod
    def get_bars(self, symbol="SHSE.rb1610", begin_time="2016-08-19 21:00:00", end_time="2016-08-20 21:00:00",
                 bar_type=60, time_out=None):
        pass

    @abstractmethod
    def get_last_n_bars(self, symbol="SHSE.rb1610", bar_type=60, n=5, time_out=None):
        pass

    @abstractmethod
    def get_daily_bars(self, symbol="SHSE.rb1610", begin_time="2016-08-19", end_time="2016-08-20", time_out=None):
        pass

    @abstractmethod
    def get_last_n_daily_bars(self, symbol="SHSE.rb1610", n=10, time_out=None):
        pass


class AbstractStrategy(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def req_login(self):
        pass

    @abstractmethod
    def req_subscribe(self, date_type, symbol):
        pass

    @abstractmethod
    def req_un_subscribe(self, data_type, symbol):
        pass

    @abstractmethod
    def req_account_detail(self, trading_day=None):
        pass

    @abstractmethod
    def req_position(self, strategy_id):
        pass

    @abstractmethod
    def req_order_list(self, strategy_id):
        pass

    @abstractmethod
    def send_order(self, symbol, bs_flag, position_effect, price_type, price, volume, strategy, hedge_type):
        pass

    @abstractmethod
    def req_cancel_order(self, order_id):
        pass


class AbstractNotifyMessageHandler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def on_notify_order_detail(self, order_detail):
        pass

    @abstractmethod
    def on_notify_quote(self, data_type, data):
        pass

    @abstractmethod
    def on_notify_connection_error(self, reason=""):
        pass

    @abstractmethod
    def on_command_strategy_exit(self, reason=None):
        pass


class TestAbsCls(unittest.TestCase):
    def test_instantiate(self):
        class TCls(AbstractStrategy):
            pass

        TCls()
