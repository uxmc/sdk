# -*- coding:utf-8 -*-
import unittest
import datetime

import logging

from sd.communication.server.protocol.function_constants import *
from sd.strategy.basestragety import BaseStrategy
from sd.strategy.bean.bean import StrategyError
from sd.strategy.bean.databean import KlineBean
from sd.strategy.kline.product_trade_sample_time import get_sample_time_point, get_real_sample_time, \
    is_instrument_in_trade_time
from sd.strategy.kline.quoteconstants import *

__author__ = 'patronfeng'
'''
如果不支持bar内更新，则值会在bar结束的时候更新一行，通知一次
如果支持bar内更新，每次tick都会有更新，如果是一个新的bar的开始，创建一个新bar，每次更新最新的bar的值

'''


def convert_str_time_2_ms_offset_of_day(tick_str_time):
    time_part = tick_str_time.split()[1]
    (hour, minutes, seconds) = time_part.split(".")[0].split(":")
    seconds = int(seconds)
    seconds += int(hour) * 3600 + int(minutes) * 60
    if len(time_part.split(".")) == 1:
        return seconds * 1000
    else:
        return seconds * 1000 + float("0." + time_part.split(".")[1]) * 1000


#
# def convert_int_time_2_second_of_day(tick_up_time):
#     return convert_int_time_2_ms_of_day(tick_up_time) / 1000
#

class DataProviderByTradeTime(BaseStrategy):
    def __init__(self, servers, user_name, pass_word, exit_handler=None):
        super(DataProviderByTradeTime, self).__init__(servers, user_name, pass_word, None,
                                                      AgentType_STRATEGY_QUOTE, None)
        self.listeners = {}
        self.ticks = {}
        self.subscribe_data = {}
        # key是DCE.i609_300表示DCE.i609, 采样周期是300秒
        # key的当前的bar
        self.concurrent_bars = {}
        self.bars = {}  # key-->history-length bars[]. key:instrument_time
        # key的当前采样时间
        self.current_sample_time = {}
        self.exit_handler = exit_handler

    '''
       订阅指定格式的数据：
            data_type，表示 tick,秒
            cyc_def 表示数据的周期
            pre_len 表示依赖的历史数据长度
            update_in_bar 表示分时数据的时候，是否在bar没有完成的时候动态更新
            数据采用tick来生成
            使用tick自带的时间戳来触发
            数据的填充发生在自然时间
    '''

    def on_notify_connection_error(self, reason=""):
        logging.error("data connection lost,exit,"+reason)
        if self.exit_handler is not None:
            self.exit_handler("data connection lost,exit,"+reason)

    def _create_bar_from_tick(self, tick, concurrent_bar_key):
        kline = KlineBean()
        kline.instrumentID = tick.instrumentID
        kline.openPrice = tick.lastPrice
        kline.volume = tick.volume
        kline.turnover = tick.turnover
        kline.closePrice = tick.lastPrice
        kline.highPrice = tick.lastPrice
        kline.lowPrice = tick.lastPrice
        kline.barType = int(concurrent_bar_key.split("_")[-1])
        current_ms = convert_str_time_2_ms_offset_of_day(tick.strTime)
        sample_point_ms = get_real_sample_time(self.current_sample_time[concurrent_bar_key])*1000
        diff_ms = current_ms - sample_point_ms
        if diff_ms < 0:
            diff_ms += 24 * 60 * 60 * 1000
        diff_ms /= 1000.0
        kline.updateTime = tick.updateTime - diff_ms
        kline.strTime = str(datetime.datetime.fromtimestamp(kline.updateTime))
        self.concurrent_bars[concurrent_bar_key] = kline

    @staticmethod
    def _convert_2_ms_time(seconds_offset_today):
        seconds = seconds_offset_today
        hour = seconds / 3600
        if hour >= 24:
            hour -= 24
        minutes = seconds % 3600 / 60
        seconds %= 60
        return 1000 * (hour * 10000 + minutes * 100 + seconds)

    def _close_bar_from_tick(self, tick, concurrent_bar_key):
        if tick is not None:
            self._update_bar_from_tick(tick, concurrent_bar_key)

    def _update_bar_from_tick(self, tick, concurrent_bar_key):
        kline = self.concurrent_bars[concurrent_bar_key]
        if tick.lastPrice > kline.highPrice:
            kline.highPrice = tick.lastPrice
        if tick.lastPrice < kline.lowPrice:
            kline.lowPrice = tick.lastPrice
        kline.closePrice = tick.lastPrice
        kline.volume = tick.volume
        kline.turnover = tick.turnover

    def _update_concurrent_bar(self, tick, cyc_def):
        standard_offset = 500
        if self._is_stock(tick.instrumentID):
            standard_offset = 3000
        # 返回更新的类型，生成的bar的内容
        current_bar_key = "%s_%d" % (tick.instrumentID, cyc_def)
        current_ms = convert_str_time_2_ms_offset_of_day(tick.strTime)
        (sample_status, current_tick_sample_time_point) = get_sample_time_point(tick.instrumentID, current_ms / 1000,
                                                                                cyc_def)
        pre_tick_sample_time_point = self.current_sample_time[current_bar_key]

        bar_status = None
        if self.concurrent_bars[current_bar_key] is None:
            # 当前不存在
            bar_status = BAR_STATUS_OPEN
            self.current_sample_time[current_bar_key] = current_tick_sample_time_point
            self._create_bar_from_tick(tick, current_bar_key)
            if cyc_def == 24 * 60 * 60:
                self.concurrent_bars[current_bar_key].openPrice = tick.openPrice
            return bar_status, None, self.concurrent_bars[current_bar_key]

        (next_tick_sample_status, next_tick_sample_time) = get_sample_time_point(tick.instrumentID,
                                                                                 (current_ms + standard_offset) / 1000,
                                                                                 cyc_def)
        close_bar = None
        if pre_tick_sample_time_point == current_tick_sample_time_point == next_tick_sample_time:
            bar_status = BAR_STATUS_UPDATE
            self._update_bar_from_tick(tick, current_bar_key)
        elif current_tick_sample_time_point == pre_tick_sample_time_point < next_tick_sample_time:
            bar_status = BAR_STATUS_CLOSE
            self._close_bar_from_tick(tick, current_bar_key)
            close_bar = self.concurrent_bars[current_bar_key]
            self.concurrent_bars[current_bar_key] = None
        elif pre_tick_sample_time_point < current_tick_sample_time_point:
            # 没有严格的按照时间来，中间有跳空. 结束前一个bar，初始下一个bar.返回的是前一个bar。
            bar_status = BAR_STATUS_CLOSE_OPEN
            # 结束当前bar
            self._close_bar_from_tick(None, current_bar_key)
            close_bar = self.concurrent_bars[current_bar_key]
            # 当前bar为None
            self.concurrent_bars[current_bar_key] = None
            # 开始一个新的bar
            self.current_sample_time[current_bar_key] = current_tick_sample_time_point
            self._create_bar_from_tick(tick, current_bar_key)
        else:
            logging.warn(
                "unknown situation, tick %s when sample, bar %s, pre_sample_point:%d,current_sample_point:%d,next_sample_point:%d",
                tick.to_json(), current_bar_key, pre_tick_sample_time_point, current_tick_sample_time_point,
                next_tick_sample_time)
            return None, None, None

        return bar_status, close_bar, self.concurrent_bars[current_bar_key]

    def _update_listen_data(self, tick):
        for key in self.listeners[tick.instrumentID].keys():
            (cyc_def, update_in_bar) = key.split("_")
            (bar_status, close_bar, current_bar) = self._update_concurrent_bar(tick, int(cyc_def))
            if bar_status is None:
                continue
            if int(update_in_bar):
                # 有bar 结束
                if bar_status == BAR_STATUS_CLOSE or bar_status == BAR_STATUS_CLOSE_OPEN:
                    for cb in self.listeners[tick.instrumentID][key]:
                        cb(int(cyc_def), close_bar, BAR_STATUS_CLOSE)
                # 如果是结束时间，current_bar 一定是None，不用通知
                if current_bar is None:
                    return
                if bar_status == BAR_STATUS_CLOSE_OPEN or bar_status == BAR_STATUS_CLOSE_OPEN:
                    for cb in self.listeners[tick.instrumentID][key]:
                        cb(int(cyc_def), current_bar, BAR_STATUS_CLOSE_OPEN)
                elif bar_status == BAR_STATUS_UPDATE:
                    for cb in self.listeners[tick.instrumentID][key]:
                        cb(int(cyc_def), current_bar, BAR_STATUS_UPDATE)
            else:
                # 有bar 结束，并且不要求bar内更新
                if bar_status == BAR_STATUS_CLOSE_OPEN or bar_status == BAR_STATUS_CLOSE:
                    for cb in self.listeners[tick.instrumentID][key]:
                        cb(int(cyc_def), close_bar, BAR_STATUS_CLOSE)
                if bar_status == BAR_STATUS_CLOSE_OPEN or bar_status == BAR_STATUS_OPEN:
                    if current_bar is None:
                        return
                    for cb in self.listeners[tick.instrumentID][key]:
                        cb(int(cyc_def), current_bar, BAR_STATUS_OPEN)

    def on_notify_quote(self, data_type, data):
        if data_type == TICK:
            concurrent_ms = convert_str_time_2_ms_offset_of_day(data.strTime)
            if not is_instrument_in_trade_time(data.instrumentID, concurrent_ms / 1000):
                return
            if data.lastPrice == 0 or data.openPrice == 0:
                logging.warn("wrong tick data:%s" % data.to_json())
                return
                # 1. 更新 tick 数据，可以获取最新的买卖手数的数据，需要存历史数据么？
            self.ticks[data.instrumentID] = data
            # 2. 更新所有和这个symbol相关联的需要更新的数据，并且通知结果
            self._update_listen_data(data)

    def get_latest_tick(self, symbol):
        if symbol in self.ticks:
            return self.ticks[symbol]
        else:
            err, data = self.get_latest_tick(symbol)
            if err.errorId != 0 and len(data) != 1:
                return None
            else:
                return data[0]

    @staticmethod
    def _is_stock(symbol):
        if symbol.split(".")[0] == "SHSE" or symbol.split(".")[0] == "SZSE":
            return True
        else:
            return False

    def un_subscribe(self, symbol, notify_cb, bar_type=1, update_in_bar=False):
        key = "%d_%d" % (bar_type, update_in_bar)
        if not self.listeners.has_key(symbol):
            return
        if not self.listeners[symbol].has_key(key):
            return
        if notify_cb in self.listeners[symbol][key]:
            self.listeners[symbol][key].remove(notify_cb)

    def subscribe(self, symbol, notify_cb, bar_type=1, update_in_bar=False):
        err = StrategyError(0, "success")
        key = "%d_%d" % (bar_type, update_in_bar)
        if not self.listeners.has_key(symbol):
            self.listeners[symbol] = {}
        if key not in self.listeners[symbol]:
            self.listeners[symbol][key] = []
        if notify_cb not in self.listeners[symbol][key]:
            self.listeners[symbol][key].append(notify_cb)
        if not self.ticks.has_key(symbol):
            self.ticks[symbol] = None
        current_bar_key = "%s_%d" % (symbol, bar_type)
        err = self.req_subscribe(TICK, symbol)
        self.current_sample_time[current_bar_key] = None
        self.concurrent_bars[current_bar_key] = None
        return err


class TestData(unittest.TestCase):
    _quote_servers = "114.55.226.119:8280"
    _user_name = u"patronfeng"
    _pass_word = u"222222"
    _strategy_id = u"your-strategy-name"
    df = DataProviderByTradeTime(_quote_servers, _user_name, _pass_word)

    def notify_cb_demo(self, cyc_def, kline, kline_status):
        print("[cycle:%d,status:%d] %s" % (cyc_def, kline_status, kline.to_json()))
        print("tick: %s" % self.df.get_latest_tick(kline.instrumentID).to_json())

    def test_generate_bar(self):
        error = self.df.init()
        # self.df.subscribe("SHFE.cu1609", self.notify_cb_demo, bar_type=3600, update_in_bar=True)
        self.df.subscribe("SHFE.rb1701", self.notify_cb_demo, bar_type=60)
        # self.df.subscribe("SHFE.cu1609", self.notify_cb_demo, bar_type=60)
        # self.df.subscribe("SHFE.ag1612", self.notify_cb_demo, bar_type=60)
        self.df.run()
