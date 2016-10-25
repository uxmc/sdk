# -*- coding:utf-8 -*-
import logging

from sd.communication.server.protocol.function_constants import *
from sd.configuration.logconfig import configure_log
from sd.strategy.simplestragety import SimpleStrategy

_user_name = u"your-user-name"
_pass_word = u"your-pass-word"
_strategy_id = "your-strategy-name"

class DemoStrategy(SimpleStrategy):
    def __init__(self, trade_servers, quote_servers, user_name, pass_word, strategy=None, description=None):
        super(DemoStrategy, self).__init__(trade_servers, quote_servers, user_name, pass_word,
                                           strategy=strategy,
                                           description=description)

    '''数据的使用说明参考DataExample.py 一般来说，策略逻辑在行情处理函数里面'''

    def on_notify_quote(self, data_type, data):
        logging.info("%s", data.to_json())

    ''''下单通知的订单交易最新情况，接收后更新状态，字段参考class StrategyOrderDetail， 判断订单执行情况'''

    def on_notify_order_detail(self, order_detail):
        logging.info("[on_notify_order_detail]:%s", order_detail.to_json())

    def on_notify_connection_error(self, reason=""):
        logging.warn("on disconnection:" + reason)

    def on_command_strategy_exit(self, reason=None):
        logging.warn("on command exit")


if __name__ == "__main__":
    configure_log("DemoStrategy.log", logging.DEBUG)
    '''description: 如果你想在网页上显示任何关于这个策略的信息，提供这个字段，如果字段是标准json格式，网页上会显示为表格。{"key":"value","key2":3}  '''
    simple_strategy = DemoStrategy(TRADE_SERVER, REAL_TIME_QUOTE_SERVER, _user_name, _pass_word, _strategy_id,
                                   description="my demo strategy")
    '''先要验证是否成功'''
    err = simple_strategy.init()
    if err.errorId != 0:
        logging.error("Failed to login,exit:%s", err.to_json())
        exit(1)

    '''查询用户的帐号详情, 字段参考class StrategyAccountDetail '''
    (result, error) = simple_strategy.req_account_detail("20160823")
    if error.errorId != 0:
        logging.error(error.to_dict())
    else:
        for item in result:
            logging.info(item.to_dict())
    ''' 查询用户的持仓详情 字段参考class StrategyPosition '''
    (result, error) = simple_strategy.req_position()
    if error.errorId != 0:
        logging.error(error.to_json())
    else:
        for item in result:
            logging.info(item.to_json())

    '''查询用户的委托的订单列表, 字段参考class StrategyOrderDetail '''
    (result, error) = simple_strategy.req_order_list()
    if error.errorId != 0:
        logging.error(error.to_json())
    else:
        for item in result:
            logging.info(item.to_json())

    '''查询用户在某个策略上的持仓详情 和查询用户持仓不同的是需要传递策略名称'''
    (result, error) = simple_strategy.req_position(simple_strategy.quoteStrategy.connectionInfo.strategyName)
    if error.errorId != 0:
        logging.error(error.to_json())
    else:
        for item in result:
            logging.info(item.to_json())

    '''查询用户在某个策略上的订单详情 和查询用户订单不同的是需要传递策略名称'''
    (result, error) = simple_strategy.req_order_list(simple_strategy.quoteStrategy.connectionInfo.strategyName)
    if error.errorId != 0:
        logging.error(error.to_json())
    else:
        for item in result:
            logging.info(item.to_json())

    '''请求数据，具体用法参考DataExample.py'''

    (data, error) = simple_strategy.get_bars(symbol="SHSE.600895", begin_time="2016-05-27 09:00:00",
                                             end_time="2016-05-27 15:00:00", bar_type=60 * 30, time_out=20)  # 获取半小时K线
    if data is not None:
        for item in data:
            print item.to_dict()

    '''订阅数据，具体用法参考DataExample.py'''
    error = simple_strategy.req_subscribe(TICK, "SHFE.rb1610")
    if error.errorId != 0:
        logging.error(error.to_json())

    '''具体运行的下单类型和价格类型参考注释字段。 返回的订单id，需要检测error， 成交状况通过 on_notify_order_detail 返回'''
    (order_id, error) = simple_strategy.send_order("SHFE.rb1701", bs_flag=BSFlag_BUY,
                                                    position_effect=PositionEffect_OPEN,
                                                    price_type=PRTP_FIX,
                                                    price=2089, volume=4)
    if error.errorId != 0:
        logging.error(error.to_json())
    else:
        logging.info("received order info %d:" % order_id)

    # (order_id, error) = simple_strategy.send_order("SHSE.600895", bs_flag=BSFlag_SELL,
    #                                                 position_effect=PositionEffect_CLOSE,
    #                                                 price_type=PRTP_FIX,
    #                                                 price=2089, volume=100)
    # if error.errorId != 0:
    #     logging.error(error.to_json())
    # else:
    #     logging.info("received order info %d:" % order_id)
    '''不要忘了这句话'''
    simple_strategy.run()
