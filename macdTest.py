import pandas as pd
import jqdata
from jqlib.technical_analysis import *



def initialize(context):
    g.security = '000001.XSHE'  # 设置要操作的股票
    set_option("use_real_price", True)  # 使用真实价格交易

    set_benchmark('000300.XSHG')  # 设置基准为沪深300

    g.macd_yesterday = 0  # 用于存储昨天的MACD值

    #交易   费用设置
    



    run_daily(handle_data, time='09:35')  # 每个交易日的9:35运行market_open函数


def handle_data(context):

    security = g.security
   
    # 计算MACD指标
    DIF, DEA, _MACD = MACD(security, check_date=context.current_dt, SHORT=6, LONG=26, MID=9)

    cash  = context.portfolio.cash  # 获取当前现金余额

        # 判断买入信号：MACD线从下向上穿过信号线
    if g.macd_yesterday < 0 and _MACD[security]>0 and cash > 0:  #因为MACD是一个字典，你调用要用security作为key 即使这个案例只有一个security
        order_target_value(security, cash)  # 全仓买入

        # 判断卖出信号：MACD线从上向下穿过信号线
    elif g.macd_yesterday > 0 and _MACD[security] < 0 and context.portfolio.positions[security].closeable_amount > 0:   #注意这里用的是可卖出仓位 嗯 很严谨 
        order_target_value(security, 0)  # 卖出，清仓

    # 更新昨天的MACD值
    g.macd_yesterday = _MACD[security]