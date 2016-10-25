# -*- coding:utf-8 -*-
import re

import logging

from sd.communication.server.protocol.function_constants import EXCHANGEID_SHSE, EXCHANGEID_SZSE, EXCHANGEID_SHFE, \
    EXCHANGEID_CZCE, EXCHANGEID_DCE, EXCHANGEID_CFFEX
from sd.strategy.kline.quoteconstants import *

__author__ = 'patronfeng'
sample_time_map = {}
trade_time_map = {}


def _adjust_tick_sec_time(tick_sec_time):
    tick_sec_time += 4 * 60 * 60
    if tick_sec_time >= 24 * 60 * 60:
        tick_sec_time -= 24 * 60 * 60
    return tick_sec_time


def get_real_sample_time(sample_sec_time):
    sample_sec_time -= 4 * 60 * 60
    if sample_sec_time < 0:
        sample_sec_time += 24 * 60 * 60
    return sample_sec_time


'''
    判断是否在交易时间段
'''


def is_instrument_in_trade_time(instrument, tick_sec_time):
    tick_sec_time = _adjust_tick_sec_time(tick_sec_time)
    trade_time = _get_trade_time(instrument)
    for i in range(0, len(trade_time) / 2):
        if trade_time[2 * i] * 60 <= tick_sec_time < trade_time[2 * i + 1] * 60:
            return True
    return False


def _is_instrument_in_sample_time(instrument, tick_sample_time, data_type):
    trade_time = _get_trade_time(instrument)
    for i in range(0, len(trade_time) / 2):
        if trade_time[2 * i] * 60 <= tick_sample_time < trade_time[2 * i + 1] * 60:
            return TRADE_TIME_OK

    # 如果超过当天的交易时间
    if tick_sample_time >= trade_time[-1]:
        return TRADE_TIME_FAILED_FINISHED
    (market, xx) = instrument.split(".")
    if market not in (EXCHANGEID_SHSE, EXCHANGEID_SZSE, EXCHANGEID_CFFEX and data_type != 24 * 60 * 60):
        # 如果有夜盘，再夜盘结束和日盘中间
        if trade_time[2] > tick_sample_time >= trade_time[1]:
            return TRADE_TIME_FAILED_BUT_NOT_FINISHED
    return TRADE_TIME_FAILED_BUT_NOT_FINISHED


'''
判断是否在指定周期的采样点
返回status--是否再交易时间，如果再交易时间，第一个采样的timestamp
    status:0 正常
    status:1 不在交易时段但是在一天的交易时间中
    status:2 不在交易时段但是再一天的交易时间中
  (status,timestamp)

  日线数据直接取tick的open， 其他时刻都用update

'''


def get_sample_time_point(instrument, tick_sec_time, data_type):
    tick_sec_time = _adjust_tick_sec_time(tick_sec_time)
    is_trade_time = _is_instrument_in_sample_time(instrument, tick_sec_time, data_type)
    sample_time = get_instrument_sample_time(instrument, data_type)
    sample_time_point = None
    for i in range(0, len(sample_time) - 1):
        if sample_time[i + 1] > tick_sec_time >= sample_time[i]:
            sample_time_point = sample_time[i]
            break
    if sample_time_point is None:
        sample_time_point = sample_time[-1]
    return is_trade_time, sample_time_point


def _get_trade_time(instrument):
    '''
    交易所的交易时间,可以根据交易所变化来修改
    保存的时候,所有时间往后推4个小时，这样夜盘也在同一天
    '''
    (market, symbol) = instrument.split(".")
    product = re.split(r'\d', symbol)[0]
    trade_time = []
    if market == EXCHANGEID_SHSE or market == EXCHANGEID_SZSE:
        return [13 * 60 + 30, 15 * 60 + 30, 17 * 60, 19 * 60]
    if product in trade_time_map:
        return trade_time_map[product]

    if market == EXCHANGEID_SHFE:
        # 上海期货交易所的交易时间 上交所9点至10点15，10点半至11点半，1点半至3点。最晚夜盘从晚上九点到到11点
        trade_time = [13 * 60, 14 * 60 + 15, 14 * 60 + 30, 15 * 60 + 30, 17 * 60 + 30, 19 * 60, 1 * 60, 3 * 60]
        if product in ["ag", "au"]:
            # 黄金、白银：21:00——次日2:30
            trade_time[7] = 6 * 60 + 30
        elif product in ["cu", "al", "zn", "pb", "ni", "sn"]:
            # 铜、铝、锌、铅,镍,锡：21:00——次日1:00
            trade_time[7] = 5 * 60
    elif market == EXCHANGEID_CZCE:
        # 郑商所的交易时间：9点至10点15，10点半至11点半，1点半至3点。夜盘从晚上9点到晚上11点半
        trade_time = [13 * 60, 14 * 60 + 15, 14 * 60 + 30, 15 * 60 + 30, 17 * 60 + 30, 19 * 60, 1 * 60,
                      3 * 60 + 30]
    elif market == EXCHANGEID_DCE:
        # 大商所的交易时间：9点至10点15，10点半至11点半，1点半至3点。夜盘从晚上9点到晚上11点半
        trade_time = [13 * 60, 14 * 60 + 15, 14 * 60 + 30, 15 * 60 + 30, 17 * 60 + 30, 19 * 60, 1 * 60,
                      3 * 60 + 30]
    elif market == EXCHANGEID_CFFEX:
        # 中金所交易时间 中金所：9点30至11点半，1点至3点15.最后交易日下午1点至3点。
        trade_time = [13 * 60 + 30, 15 * 60 + 30, 17 * 60, 19 * 60 + 15]
        # 国债期货是到3点15！！！！！！！！
    trade_time.sort()
    trade_time_map[product] = trade_time
    return trade_time


def get_instrument_sample_time(instrument, datatype):
    trade_time = _get_trade_time(instrument)
    (market, tt) = instrument.split(".")
    product = re.split(r'\d', tt)[0]
    key = "%s_%d" % (product, datatype)
    if key in sample_time_map:
        return sample_time_map[key]
    day_time = trade_time
    night_time = []
    if market not in (EXCHANGEID_SHSE, EXCHANGEID_SZSE, EXCHANGEID_CFFEX):
        day_time = trade_time[2:]
        night_time = trade_time[0:2]
    sample_time = []
    for item in [day_time, night_time]:
        current_trade_seconds = 0
        for i in range(0, len(item) / 2):
            current_offset_in_current_trade_time = item[2 * i] * 60
            end_sample_time = item[2 * i + 1] * 60
            while current_offset_in_current_trade_time < end_sample_time:
                if current_trade_seconds % datatype == 0:
                    sample_time.append(current_offset_in_current_trade_time)
                current_offset_in_current_trade_time += 1
                current_trade_seconds += 1
    sample_time.sort()
    if datatype == 24 * 60 * 60:
        sample_time = [trade_time[0] * 60]
    '''如果有特殊的采样需要,可以入下配置,用的是一天的秒数,并且加了4个小时「「「」」」'''
    if datatype == 3600:
        if market == EXCHANGEID_SHFE:
            sample_time_map[key] = [3600, 7200, 10800, 14400, 18000, 21600, 46800, 50400, 54000, 64800]
        elif market == EXCHANGEID_CZCE or market == EXCHANGEID_DCE:
            sample_time_map[key] = [3600, 7200, 10800, 46800, 50400, 54000, 64800]
    elif datatype == 1800:
        if market == EXCHANGEID_SHFE:
            sample_time_map[key] = [3600, 5400, 7200, 9000, 10800, 12600, 14400, 16200, 18000, 19800, 21600, 46800,
                                    48600, 50400, 52200, 54000, 63000, 64800, 66600]
        elif market == EXCHANGEID_CZCE or market == EXCHANGEID_DCE:
            sample_time_map[key] = [3600, 5400, 7200, 9000, 10800, 46800, 48600, 50400, 52200, 54000, 63000, 64800,
                                    66600]
    elif datatype == 7200:
        if market == EXCHANGEID_SHFE:
            sample_time_map[key] = [3600, 10800, 18000, 46800, 54000]
        elif market == EXCHANGEID_CZCE or market == EXCHANGEID_DCE:
            sample_time_map[key] = [3600, 46800, 54000]
    else:
        sample_time_map[key] = sample_time

    logging.info("sample time for " + key + " is :" + str(sample_time_map[key]))
    return sample_time_map[key]


if __name__ == "__main__":
    print get_instrument_sample_time("DCE.i1612", 3600)
