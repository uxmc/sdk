# encoding: utf-8
from __future__ import with_statement
from __future__ import absolute_import

import logging

from sd.strategy.basestragety import BaseStrategy
from sd.strategy.bean.bean import StrategyOrderDetail
from sd.communication.server.protocol.function_constants import *

'''
        获取策略下的某个合约的方向,基于如下假设:
           1. 必须有策略id
           2. 用户在一个策略上只想持有一个方向的持仓
           3. 用户可能在界面上下单,也可能通过程序下单
        如何确定用户想持有的持仓方向:
           1. 如果今天有订单,根据今天的最新的开仓订单来确定
           2. 如果今天没有订单,根据持仓来确定
           3. 如果有多个持仓,根据持有多的来确定
           4. 如果也没有持仓,那方向为空
'''


class SingleDirectionStrategy(BaseStrategy):
    def __init__(self, servers, user_name, pass_word, strategy=None, usage_type=AgentType_STRATEGY_TRADE,
                 description=None):
        super(SingleDirectionStrategy, self).__init__(servers, user_name, pass_word, strategy, usage_type,
                                                      description)
        self.strategy_orders = {}
        self.strategy_positions = {}  # 合约_direction
        self.user_account_details = {}

    def get_strategy_position(self, instrument_id, bs_flag):
        return self.strategy_positions.get("%s_%d" % (instrument_id, bs_flag), None)

    def get_strategy_opposite_position(self, instrument_id, bs_flag):
        return self.strategy_positions.get("%s_%d" % (instrument_id, bs_flag * -1), None)

    def get_strategy_order(self, order_id):
        return self.strategy_orders.get(order_id, None)

    def get_strategy_instrument_holding_direction(self, instrument):
        latest_order = None
        for item in self.strategy_orders.values():
            if item.instrumentID == instrument and item.bsFlag == PositionEffect_OPEN and (
                            item.orderStatus not in (
                                ORDER_STATUS_INVALID, ORDER_STATUS_SUCCEEDED) or item.tradedVolume != 0):
                latest_order = item if latest_order is None else latest_order
                latest_order = item if latest_order.orderId < item.orderId else latest_order
        if latest_order is not None:
            return latest_order.bsFlag
        position_buy = self.get_strategy_position(instrument, BSFlag_BUY)
        position_sell = self.get_strategy_position(instrument, BSFlag_SELL)
        if position_buy is not None and position_sell is None and position_buy.yesterdayPosition + position_buy.todayPosition > 0:
            return BSFlag_SELL
        if position_buy is None and position_sell is not None and position_sell.yesterdayPosition + position_sell.todayPosition > 0:
            return BSFlag_BUY
        if position_buy is not None and position_sell is not None:
            if position_buy.yesterdayPosition + position_buy.todayPosition > position_sell.yesterdayPosition + position_sell.todayPosition:
                return BSFlag_BUY
            elif position_buy.yesterdayPosition + position_buy.todayPosition < position_sell.yesterdayPosition + position_sell.todayPosition:
                return BSFlag_SELL
        return None

    def req_order_list(self, strategy_name):
        result, err = super(SingleDirectionStrategy, self).req_order_list(strategy_name)
        if strategy_name == self.strategyConnectionInfo.strategyName and err.errorId != 0 and result is not None:
            for strategy_order in result:
                self.strategy_orders[strategy_order.orderId] = strategy_order
        return result, err

    def req_account_detail(self, trading_day=None):
        result, err = super(SingleDirectionStrategy, self).req_account_detail(trading_day)
        if trading_day is None and err.errorId != 0 and result is not None:
            for account in result:
                self.user_account_details[account.accountName] = account
        return result, err

    def req_position(self, strategy_id=None):
        result, err = super(SingleDirectionStrategy, self).req_position(strategy_id)
        if strategy_id == self.strategyConnectionInfo.strategyName and err.errorId != 0 and result is not None:
            for strategy_position in result:
                self.strategy_positions[
                    "%s_%d" % (strategy_position.instrument, strategy_position.bsFlag)] = strategy_position
        return result, err

    def notify_st_order_detail_handler(self, async_message):
        try:
            logging.debug(u"return orderdetail: %s", async_message.body)
            strategy_order_detail = StrategyOrderDetail().from_json(async_message.body)
            self.strategy_orders[strategy_order_detail.orderId] = strategy_order_detail
            self.externalNotifyMessageHandler.on_notify_order_detail(strategy_order_detail)
            self.req_position(self.connectionInfo.strategyName)
        except Exception, e:
            logging.exception(e)

    def req_login(self):
        err = super(SingleDirectionStrategy, self).req_login()
        if err.errorId != 0:
            self.req_position(self.connectionInfo.strategyName)
            self.req_order_list(self.connectionInfo.strategyName)
        return err
