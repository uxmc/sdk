# -*- coding:utf-8 -*- 
__author__ = 'patronfeng'
PRTP_OFFSET_TICK_NUMBER = 15


# 新的bar开始
BAR_STATUS_OPEN = 1
# bar在周期内tick更新
BAR_STATUS_UPDATE = 0
# bar结束
BAR_STATUS_CLOSE = 2
# 对外不会看到，表示一个tick导致了前一个bar结束，后一个bar开始，用于数据不连续规范场景
BAR_STATUS_CLOSE_OPEN = 3


TRADE_TIME_OK = 0
TRADE_TIME_FAILED_BUT_NOT_FINISHED = 1
TRADE_TIME_FAILED_FINISHED = 2
