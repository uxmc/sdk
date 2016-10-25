# encoding: utf-8

from __future__ import absolute_import

from sd.utils.bean import BaseBean



class KlineBean(BaseBean):
    def __init__(self,
        exchange = None,
        instrumentID = None,
        barType = None,
        strTime = None,
        updateTime = None,
        openPrice = None,
        highPrice = None,
        lowPrice = None,
        closePrice = None,
        volume = None,
        turnover = None,
        preClosePrice = None,
        position = None,
        adjFactor = None,
        flag = None):

        self.exchange = exchange
        self.instrumentID = instrumentID
        self.barType = barType
        self.strTime = strTime
        self.updateTime = updateTime
        self.openPrice = openPrice
        self.highPrice = highPrice
        self.lowPrice = lowPrice
        self.closePrice = closePrice
        self.volume = volume
        self.turnover = turnover
        self.preClosePrice = preClosePrice
        self.position = position
        self.adjFactor = adjFactor
        self.flag = flag


class DailyKLineBean(BaseBean):
    def __init__(self,
         exchange=None,
         instrumentID=None,
         barType=None,
         strTime=None,
         updateTime=None,
         openPrice=None,
         highPrice=None,
         lowPrice=None,
         closePrice=None,
         volume=None,
         turnover=None,
         position=None,
         settlePrice=None,
         upperLimitPrice=None,
         lowerLimitPrice=None,
         preClosePrice=None,
         adjFactor=None,
         flag=None
                 ):
        self.exchange = exchange  # 交易所代码 =
        self.instrumentID = instrumentID  # 证券ID =
        self.barType = barType  # bar类型，以秒为单位，比如1分钟bar =  bar_type=60
        self.strTime = strTime  # 可视化时间
        self.updateTime = updateTime  # 行情时间戳
        self.openPrice = openPrice
        self.highPrice = highPrice
        self.lowPrice = lowPrice
        self.closePrice = closePrice
        self.volume = volume
        self.turnover = turnover
        self.position = position  # 仓位 =
        self.settlePrice = settlePrice  # 结算价
        self.upperLimitPrice = upperLimitPrice  # 涨停价
        self.lowerLimitPrice = lowerLimitPrice  # /跌停价
        self.preClosePrice = preClosePrice
        self.adjFactor = adjFactor  # 复权因子
        self.flag = flag  # 除权出息标记

class TickBean(BaseBean):
    def __init__(self,
            exchange=None,
            instrumentID=None,
            updateTime=None,
            strTime=None,
            lastPrice=None,
            openPrice=None,
            highPrice=None,
            lowPrice=None,
            volume=None,
            turnover=None,
            position=None,
            upperLimitPrice=None,
            lowerLimitPrice=None,
            settlePrice=None,
            preClosePrice=None,
            askPrice=None,
            askVolume=None,
            bidPrice=None,
            bidVolume=None):
        self.exchange = exchange
        self.instrumentID = instrumentID
        self.updateTime = updateTime
        self.strTime = strTime
        self.lastPrice = lastPrice
        self.openPrice = openPrice
        self.highPrice = highPrice
        self.lowPrice = lowPrice
        self.volume = volume
        self.turnover = turnover
        self.position = position
        self.upperLimitPrice = upperLimitPrice
        self.lowerLimitPrice = lowerLimitPrice
        self.settlePrice = settlePrice
        self.preClosePrice = preClosePrice
        self.askPrice = askPrice
        self.askVolume = askVolume
        self.bidPrice = bidPrice
        self.bidVolume = bidVolume
