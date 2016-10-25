# -*- coding:utf-8 -*-
import logging

from sd.communication.server.protocol.function_constants import AgentType_STRATEGY_QUOTE, TICK, BAR, DAILY_BAR, \
    REAL_TIME_QUOTE_SERVER
from sd.strategy.basestragety import BaseStrategy
from sd.configuration.logconfig import configure_log


#  配置日志文件，输出到内容dataexample.log
_user_name = u"your-strategy-name"
_pass_word = u"your-pass-word"
_strategy_id = None


class DataExample(BaseStrategy):
    def __init__(self, servers, user_name, pass_word, strategy=None, description=None):
        super(DataExample, self).__init__(servers, user_name, pass_word, strategy,
                                          AgentType_STRATEGY_QUOTE, description)

    '''
        定义返回的数据的数据结构，只有两个：KLineBean， TickBean，DailyKLineBean 数据结构见楼上databean.py
    '''

    def on_notify_quote(self, data_tye, data):
        if data_tye == TICK:
            logging.info("Received tick data:%s", data.to_dict())
        elif data_tye == BAR:
            logging.info("Received bar data:%s", data.to_dict())
        elif data_tye == DAILY_BAR:
            logging.info("Received daily bar data:%s", data.to_dict())

        else:
            logging.warn("Unexpected data type:%d,content:%s", data_tye, data.to_dict())


if __name__ == "__main__":
    configure_log("dataexample.log", logging.DEBUG)
    reqDataTerminal = BaseStrategy(REAL_TIME_QUOTE_SERVER, _user_name, _pass_word)
    err = reqDataTerminal.init()
    if err.errorId != 0:
        logging.error("Failed to login,exit, %s", err.to_json())
        exit(1)
    (data,error) = reqDataTerminal.get_bars(symbol="SHFE.rb1610", begin_time="2016-05-27 09:00:00",
                                             end_time="2016-05-27 15:00:00", bar_type=60, time_out=20)  # 获取60秒K线
    for item in data:
        print item.to_json()

    (data,error)  = reqDataTerminal.get_bars(symbol="SHSE.600895", begin_time="2016-05-27 09:00:00",
                                             end_time="2016-05-27 15:00:00", bar_type=60 * 30, time_out=20)  # 获取半小时K线
    for item in data:
        print item.to_json()
    (data,error) = reqDataTerminal.get_last_n_bars(symbol="SHSE.600895", n=10, bar_type=60 * 30,
                                                    time_out=20)  # 获取最新的10根半小时K线
    for item in data:
        print item.to_json()
    (data,error) = reqDataTerminal.get_last_n_daily_bars(symbol="SHSE.600895", n=10, time_out=20)  # 获取最新的10根日线
    for item in data:
        print item.to_json()
    (data,error) = reqDataTerminal.get_daily_bars(symbol="SHFE.rb1610", begin_time="2016-05-27",
                                             end_time="2016-05-27",time_out=20)  # 获取指定范围的日K线
    for item in data:
        print item.to_json()
    (data,error) = reqDataTerminal.get_last_n_ticks(symbol="SHSE.600895", n=10, time_out=20)  # 获取最新的10个tick数据
    for item in data:
        print item.to_json()
    (data,error) = reqDataTerminal.get_ticks(symbol="SHFE.rb1610", begin_time="2016-05-27 09:00:00",
                                              end_time="2016-05-27 15:00:00", time_out=20)  # 获取指定时间范围的tick数据
    for item in data:
        print item.to_json()
    (data,error) = reqDataTerminal.get_last_ticks(symbol=["SHFE.rb1610", "SHSE.600895"], time_out=20)  # 获取合约列表的最新tick
    for item in data:
        print item.to_json()
    (data,error) = reqDataTerminal.get_last_ticks(symbol="SHSE.600895", time_out=20)  # 获取指定单个合约的最新tick
    for item in data:
        print item.to_json()
    ###  如果不需要订阅数据，不用重写BaseStrategy
    dataExample = DataExample(REAL_TIME_QUOTE_SERVER, _user_name, _pass_word)
    # 任何登录需要判断登录是否成功
    err = dataExample.init()
    if err.errorId != 0:
        logging.error("Failed to login,exit, %s", err.to_json())
        exit(1)
    # #######订阅上期所tick行情
    symbol = "%s.%s" % ("DCE", "l1701")
    ret = dataExample.req_subscribe(TICK, symbol)
    if ret.errorId != 0:
        logging.error("Failed to subscribe %s because of %s", symbol, ret.to_json())
    ret = dataExample.req_subscribe(TICK, "SHFE.rb1701")
    ret = dataExample.req_subscribe(TICK, "SHSE.601003")
    if ret.errorId != 0:
        logging.error("Failed to subscribe %s because of %s", symbol, ret.to_json())
    ###### 定义的内容可以通过 on_notify_quote(self, data_tye, data) 接收数据--data_type：数据类型; data 是数据

    ########## 请求历史分时bar行情
    (data,error) = reqDataTerminal.get_bars(symbol="SHSE.600895", begin_time="2016-05-27 09:00:00",
                                             end_time="2016-05-27 15:00:00", bar_type=60 * 60, time_out=20)  # 获取1小时K线
    for item in data:
        print item.to_json()
    if error.errorId == 0:
        ###遍历所有的数据
        for bar in data:
            print bar.to_json()
    else:
        ########打印错误内容
        logging.error(error.to_json())
    dataExample.run()
