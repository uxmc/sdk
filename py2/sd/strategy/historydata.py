# -*- coding:utf-8 -*-
import urllib
import urllib2
import json
import unittest

import logging

from sd.communication.server.protocol.function_constants import HISTORY_QUOTE_SERVER
from sd.strategy.bean.bean import StrategyError
from sd.strategy.bean.databean import TickBean, KlineBean, DailyKLineBean
from sd.strategy.interface import HistoryDataInterface

__author__ = 'patronfeng'


def _json_convert_to_bean(json_list, bean_class):
    ret = []
    if json_list is None:
        return ret
    for item in json_list:
        ret.append(bean_class().from_dict(item))
    return ret


class HistoryData(HistoryDataInterface):
    def __init__(self, user_name=None, pass_word=None, quote_server=HISTORY_QUOTE_SERVER, time_out=20):
        self.userName = user_name
        self.passWord = pass_word
        self.server = quote_server
        self.timeOut = time_out
        if self.timeOut is None:
            self.timeOut = 20

    def get_ticks(self, symbol="SHSE.rb1610", begin_time="2016-08-19 21:00:00", end_time="2016-08-20 21:00:00",
                  time_out=None):
        error, data = self._rpc_call("get_ticks",
                                     "symbols=%s&begin_time=%s&end_time=%s" % (symbol, begin_time, end_time), time_out)
        if error.errorId != 0:
            return data, error
        return _json_convert_to_bean(data, TickBean),error

    def get_last_ticks(self, symbol=None, time_out=None):
        if not symbol:
            symbol = []
        if not isinstance(symbol, list):
            symbol = [symbol]
        error, data = self._rpc_call("get_last_ticks",
                                     "symbols=%s" % (",".join(symbol)), time_out)
        if error.errorId != 0:
            return data, error
        return _json_convert_to_bean(data, TickBean),error

    def get_last_n_ticks(self, symbol, n, time_out=None):
        error, data = self._rpc_call("get_last_n_ticks",
                                     "symbol=%s&n=%d" % (symbol, n), time_out)
        if error.errorId != 0:
            return data, error
        return _json_convert_to_bean(data, TickBean),error

    def get_bars(self, symbol="SHSE.rb1610", begin_time="2016-08-19 21:00:00", end_time="2016-08-20 21:00:00",
                 bar_type=60, time_out=None):
        error, data = self._rpc_call("get_bars",
                                     "symbols=%s&begin_time=%s&end_time=%s&bar_type=%d" % (
                                         symbol, begin_time, end_time, bar_type), time_out)
        if error.errorId != 0:
            return data, error
        return _json_convert_to_bean(data, KlineBean),error

    def get_last_n_bars(self, symbol="SHSE.rb1610", bar_type=60, n=5, time_out=None):
        error, data = self._rpc_call("get_last_n_bars",
                                     "symbol=%s&bar_type=%d&n=%d" % (symbol, bar_type, n), time_out)
        if error.errorId != 0:
            return data, error
        return _json_convert_to_bean(data, KlineBean),error

    def get_daily_bars(self, symbol="SHSE.rb1610", begin_time="2016-08-19", end_time="2016-08-20", time_out=None):
        error, data = self._rpc_call("get_dailybars",
                                     "symbols=%s&begin_time=%s&end_time=%s" % (
                                         symbol, begin_time, end_time), time_out)
        if error.errorId != 0:
            return data, error
        return _json_convert_to_bean(data, DailyKLineBean),error

    def get_last_n_daily_bars(self, symbol="SHSE.rb1610", n=10, time_out=None):
        error, data = self._rpc_call("get_last_n_dailybars",
                                     "symbol=%s&n=%d" % (symbol, n), time_out)
        if error.errorId != 0:
            return data, error
        return _json_convert_to_bean(data, DailyKLineBean),error

    def _rpc_call(self, url, parameters, time_out=None):
        try:
            if time_out is None:
                time_out = self.timeOut
            error = StrategyError()
            data = None
            req_data = {}
            values = "appplt=web&%s&userName=%s&passWord=%s" % (parameters, self.userName, self.passWord)
            for item in values.split("&"):
                key, val = item.split("=")
                req_data[key] = val
            req_data = urllib.urlencode(req_data)
            response = urllib2.urlopen("http://%s/quotehistory/v1/data/%s?%s" % (self.server, url, req_data),
                                       timeout=time_out)
            if response.code != 200:
                logging.warn("failed to get data as status:%d reason:%s" % (response.code, response.msg))
                error.errorId = response.code
                error.errorMsg = "failed to get data as status:%d reason:%s" % (response.code, response.msg)
                return error, data
            str_data = response.read()

            if len(str_data) == 0:
                logging.warn("failed to get data as response data is %s" % str_data)
                error.errorId = 200
                error.errorMsg = "failed to get data as response data is %s" % str_data
                return error, data
            json_data = json.loads(str_data)
            if json_data["err"] != 0:
                error.errorId = int(json_data['errCode'])
                error.errorMsg = "failed to get data as error:%s" % json_data['errCode']
                return error, data
            error.errorId = 0
            error.errorMsg = "success"
            if "data" not in json_data:
                error.errorId = 0
                error.errorMsg = "no content"
                return error, data
            return error, json_data['data']
        except Exception, e:
            logging.exception(e)
            return StrategyError(500, "internal error"), None


class TestHistoryData(unittest.TestCase):
    history_data = HistoryData(user_name="uxmc", pass_word="111111")

    def test_history(self):
        # error,data = self.history_data.get_bars("SHFE.ag1612",begin_time="2016-09-10 15:00:00",end_time="2016-09-26 15:00:00",bar_type=60*60)
        # print "get_bars:"
        # for item in data:
        #     print(item.to_json())
        # error, data = self.history_data.get_ticks("SHFE.ag1612", begin_time="2016-09-23 14:00:00",
        #
        #                                end_time="2016-09-23 15:00:00")
        # print "get_ticks:"
        # for item in data:
        #     print(item.to_json())

        data,error = self.history_data.get_daily_bars("SHFE.ag1612", begin_time="2016-09-10", end_time="2016-09-06")
        print "get_daily_bars:"
        for item in data:
            print(item.to_json())
        data,error = self.history_data.get_last_ticks("SHFE.ag1612")
        print "get_last_ticks:"
        for item in data:
            print(item.to_json())
        edata,error = self.history_data.get_last_ticks(["SHFE.ag1612", "DCE.m1701"])
        print "get_last_ticks:"
        for item in data:
            print(item.to_json())
        data,error = self.history_data.get_last_n_ticks("SHFE.ag1612", 40)
        print "get_last_n_ticks:"
        for item in data:
            print item.to_json()
        data,error = self.history_data.get_last_n_bars("SHFE.ag1612", 300, n=10)
        print "get_last_n_bars:"
        for item in data:
            print item.to_json()

        data,error = self.history_data.get_last_n_daily_bars("CZCE.TA701", n=4)
        print "get_last_n_daily_bars"
        for item in data:
            print(item.to_json())

        data,error = self.history_data.get_last_n_ticks("SHFE.rb1701", 40)
        print "get_last_n_ticks:"
        for item in data:
            print item.to_json()
