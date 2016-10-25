# encoding: utf-8
from __future__ import absolute_import
import unittest
import uuid

from sd.utils.bean import BaseBean
from sd.utils.typing import List

__author__ = u'yonka'


class StrategyPosition(BaseBean):
    def __init__(
            self,
            userName=None,  # 用户名
            userId=None,  # 用户id
            tradingDay=None,  # 交易日
            exchange=None,  # 交易所
            exchangeName=None,  # 交易所名字
            strategyId=None,  # 策略id-不一定有-str
            strategyName=None,
            bsFlag=None,  # 方向
            product=None,  # 产品名-比如rb
            instrument=None,  # 合约-比如SHFE.rb1610
            instrumentName=None,  # 合约名字
            yesterdayPosition=0,  # 昨仓
            todayPosition=0,  # 今仓
            closeProfit=None,  # 平仓盈亏
            floatProfit=0,  # 浮动盈亏
            avgPrice=0,  # 均价
            settlementPrice=0,  # 结算价
            lastSettlePrice=0,  # 昨日结算价
            usedCommission=0,  # 手续费
            usedMargin=0,  # 保证金
            marketValue=0,  # 市值
            assertType=0,  # 资产类型
            createTime=0,  # 创建时间
            updateTime=0,
            frozenVolume=0,  # 冻结手数目,上期所表示冻结的昨仓
            frozenTodayVolume=0,  # 冻结今仓手数目,上期所使用
            positionCost=0.0
    ):
        self.userId = userId  # 用户id
        self.tradingDay = tradingDay  # 交易日
        self.exchange = exchange  # 交易所
        self.exchangeName = exchangeName  # 交易所名字
        self.strategyId = strategyId  # 策略id-不一定有-str
        self.bsFlag = bsFlag  # 方向
        self.product = product  # 产品名-比如rb
        self.instrument = instrument  # 合约-比如SHFE.rb1610
        self.instrumentName = instrumentName  # 合约名字
        self.yesterdayPosition = yesterdayPosition  # 昨仓
        self.todayPosition = todayPosition  # 今仓
        self.closeProfit = closeProfit  # 平仓盈亏
        self.floatProfit = floatProfit  # 浮动盈亏
        self.avgPrice = avgPrice  # 均价
        self.settlementPrice = settlementPrice  # 结算价
        self.lastSettlePrice = lastSettlePrice  # 昨日结算价
        self.usedCommission = usedCommission  # 手续费
        self.usedMargin = usedMargin  # 保证金
        self.marketValue = marketValue  # 市值
        self.createTime = createTime  # 创建时间
        self.updateTime = updateTime
        self.userName = userName
        self.strategyName = strategyName
        self.assertType = assertType
        self.frozenVolume = frozenVolume
        self.frozenTodayVolume = frozenTodayVolume
        self.positionCost = positionCost


class StrategyOrderDetail(BaseBean):
    def __init__(
            self,
            orderId=None,  # 订单ID，long
            userId=None,  # 用户id
            userName=None,
            strategyId=None,  # 策略ID,
            strategyName=None,
            instrument=None,  # 合约ID，str，SHFE.rb1610
            instrumentName=None,  # 合约名字
            orderPrice=None,  # 下单价格
            orderPriceType=None,  # 下单价格类型
            volumeOriginal=None,  # 下单手数
            bsFlag=0,  # 下单方向，买还是卖
            positionEffect=0,  # 期货开平标识
            hedgeFlag=None,  # 期货对冲标识
            exchange=0,  # 交易所
            exchangeOrderId=0,  # 交易所订单id
            tradePrice=0,  # 成交均价
            tradedVolume=0,  # 成交手数
            tradedAmount=0.0,  # 成交金额
            orderStatus=0,  # 订单状态，int
            tradingDay=0,  # 交易日
            createTime=None,  # 订单创建时间
            errorMsg=None,
            orderType=None,  # 订单类型,int
            extentOrderInfo=None  # 扩展订单信息,str,json

    ):
        self.orderId = orderId  # 订单ID，long
        self.userId = userId
        self.strategyName = strategyName
        self.strategyId = strategyId  # 合约ID
        self.instrument = instrument  # 合约ID，str，SHFE.rb1610
        self.instrumentName = instrumentName  # 合约名字
        self.orderPrice = orderPrice  # 下单价格
        self.orderPriceType = orderPriceType  # 下单价格类型
        self.volumeOriginal = volumeOriginal  # 下单手数
        self.bsFlag = bsFlag  # 下单方向，买还是卖
        self.positionEffect = positionEffect  # 期货开平标识
        self.hedgeFlag = hedgeFlag  # 期货对冲标识
        self.exchange = exchange  # 交易所
        self.exchangeOrderId = exchangeOrderId  # 交易所订单id
        self.tradePrice = tradePrice  # 成交均价
        self.tradedVolume = tradedVolume  # 成交手数
        self.tradedAmount = tradedAmount  # 成交金额
        self.orderStatus = orderStatus  # 订单状态，int
        self.tradingDay = tradingDay  # 交易日
        self.createTime = createTime  # 订单创建时间
        self.errorMsg = errorMsg
        self.orderType = orderType
        self.extentOrderInfo = extentOrderInfo
        self.userName = userName


class StrategyAccountDetail(BaseBean):
    def __init__(
            self=None,
            brokerId=None,
            accountName=None,
            userName=None,
            userId=None,
            withdrawQuota=None,  # // /可取资金
            available=None,  ###可用资金
            closeProfit=None,  ##### 平仓盈亏
            positionProfit=None,  ##### 持仓盈亏费
            deposit=None,  ##### 入金
            withdraw=None,  ##### 出金
            preBalance=None,  ##### 期初权益
            frozenMargin=None,  #####冻结保证金
            frozenCommission=None,
            commission=None,  ##### 已用手续费
            currMargin=None,  ##### 当前占用保证金
            balance=None,  ##### 动态总权益
            createTime=None,  #####创建日
            updateTime=None,  ### 更新时间
            assertType=None,
            tradingDay=None  ###当前交易日

    ):
        self.accountName = accountName
        self.tradingDay = tradingDay  #####交易日
        self.available = available  ##### 可用资金
        self.balance = balance  ##### 动态总权益
        self.frozenMargin = frozenMargin  #####冻结保证金
        self.frozenCommission = frozenCommission
        self.preBalance = preBalance  ##### 期初权益
        self.commission = commission  ##### 已用手续费
        self.positionProfit = positionProfit  ##### 持仓盈亏费
        self.closeProfit = closeProfit  ##### 平仓盈亏
        self.currMargin = currMargin  ##### 当前占用保证金
        self.deposit = deposit  ##### 入金
        self.withdraw = withdraw  ##### 出金
        self.assertType = assertType
        self.createTime = createTime
        self.updateTime = updateTime
        self.userId = userId
        self.userName = userName
        self.brokerId = brokerId
        self.withdrawQuota = withdrawQuota


class StrategyError(BaseBean, RuntimeError):
    def __init__(
            self,
            error_id=0,
            error_msg=None
    ):
        self.errorId = error_id
        self.errorMsg = error_msg


class StrategyConnectionInfo(BaseBean):
    def __init__(
            self,
            account_id=None,
            strategy_id=None,
            password=None,
            description=None,
            session_id=None,
            mode=1,
            base_money=None,
            start_time=None,
            end_time=None,
            symbol='',
            commission_ratio=None,
            adjust_price_type=0

    ):
        self.userName = account_id
        self.strategyName = strategy_id
        self.password = password
        self.description = description
        self.sessionId = session_id
        self.mode = mode
        self.baseMoney = base_money
        self.startTime = start_time
        self.endTime = end_time
        self.symbol = symbol
        self.commissionRatio = commission_ratio
        self.adjustPriceType = adjust_price_type


class StrategyCancelOrder(BaseBean):
    def __init__(
            self,
            account_id=None,
            request_id=0,
            order_id=None,
    ):
        self.userName = account_id
        self.requestId = request_id
        self.orderId = order_id

class StrategyOrder(BaseBean):
    def __init__(
            self,
            userName=None,
            price=0,
            volume=0,
            strategyName=None,
            instrument=None,
            priceType=None,
            hedgeFlag=None,
            bsFlag=None,
            positionEffect=None,
            orderTime=None
    ):
        self.userName = userName
        self.price = price
        self.volume = volume
        self.strategyName = strategyName
        self.instrument = instrument  # SHSE.000600
        self.priceType = priceType
        self.hedgeFlag = hedgeFlag
        self.bsFlag = bsFlag
        self.positionEffect = positionEffect
        self.userOrderUuid = str(uuid.uuid1())
        self.orderTime = orderTime  #表示什么时候下单,只用于回测


class TestBean(unittest.TestCase):
    def test_set_StrategyFinanceAccountDetail(self):
        self.test_init_StrategyFinanceAccountDetail()

    def test_from_methods(self):
        class A(BaseBean):
            def __init__(self, a=0):
                self.a = a

            def __str__(self):
                return u"A(a=%d)" % self.a

        class B(BaseBean):
            _types = {
                u"a_list": List[A]
            }

            def __init__(self, a_list=None):
                self.a_list = a_list

        # s = "{\"a\":1}"
        s = u"""{"a":1}"""
        s1 = u"{\"a_list\":[{\"a\":1},{\"a\":2}]}"
        a = A().from_json(s)
        print a
        b = B().from_json(s1)
        print b.a_list, b.a_list[0]

        print a.to_json()
        print b.to_json()
