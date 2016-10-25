# -*- coding:utf-8 -*- 
__author__ = 'patronfeng'
REAL_TIME_QUOTE_SERVER = "mock.realtime.quote.uxmc.cn:8280"
HISTORY_QUOTE_SERVER = "mock.history.quote.uxmc.cn:8123"
TRADE_SERVER = "mock.trade.uxmc.cn:8290"
# /**********连接类型常量值**************/
AgentType_STRATEGY_TRADE = 1
AgentType_STRATEGY_QUOTE = 2


# /**********期货对冲常量值**************/
HEDGE_FLAG_SPECULATION = 49
HEDGE_FLAG_ARBITRAGE = 50
HEDGE_FLAG_HEDGE = 51


# /**********下单方向**************/
BSFlag_BUY = 1
BSFlag_SELL = -1

# /**********订单对持仓的影响**************/

PositionEffect_OPEN = 0
PositionEffect_CLOSE = 1
PositionEffect_CLOSE_TODAY = 2
PositionEffect_CLOSE_YESTERDAY = 3

# /**********交易所**************/
EXCHANGEID_SHFE = "SHFE"  # 上期所
EXCHANGEID_DCE = "DCE"  # 大商所
EXCHANGEID_CFFEX = "CFFEX"  # 中金所
EXCHANGEID_CZCE = "CZCE"  # 郑商所
EXCHANGEID_SHSE = "SHSE"  # 上海股票交易所
EXCHANGEID_SZSE = "SZSE"  # 深圳股票交易所



# /**********数据类型**************/
TICK = 5

BAR = 20

DAILY_BAR = 50




# /**********订单状态**************/	
ORDER_STATUS_CREATED = 10  # 创建订单
ORDER_STATUS_UNREPORTED = 13  # 订单待确认
ORDER_STATUS_REPORTED = 15  # 订单已确认
ORDER_STATUS_NOT_TRADE = 16  # 未成交
ORDER_STATUS_PART_SUCC = 17  # 部分成交
ORDER_STATUS_SUCCEEDED = 19  # 交易成交
ORDER_STATUS_UNREPORTED_CANCEL = 20  # 取消订单待确认
ORDER_STATUS_REPORTED_CANCEL = 23  # 取消订单已确认
ORDER_STATUS_INVALID = 30  # 废单
ORDER_STATUS_CANCELED = 54  # 取消成功
# /**********价格类型常量值**************/
# PRTP_SALE5 = 0
# PRTP_SALE4 = 1
# PRTP_SALE3 = 2
# PRTP_SALE2 = 3
# PRTP_SALE1 = 4
# PRTP_LATEST = 5
# PRTP_BUY1 = 6
# PRTP_BUY2 = 7
# PRTP_BUY3 = 8
# PRTP_BUY4 = 9
# PRTP_BUY5 = 10
PRTP_FIX = 11  # 限价单
PRTP_MARKET = 12  # 市价单
PRTP_OPPOSIT = 13  # 对手价格
