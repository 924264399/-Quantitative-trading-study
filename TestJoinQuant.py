
def initialize(context):
    g.security = "000001.XSHE"  # 平安银行
    run.daily(market_open,time = 'every_day')  # 每个bar都执行一次handle_data函数

    set_benchmark('000300.XSHG')  # 以沪深300指数为基准
    set_option('use_real_price', True) # 使用真实价格交易

    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')  # 设置交易费用
    set_slippage(PriceSlippage(percent=0.002), type='stock') # 设置滑点
    set_option('order_volume_ratio', 0.2)  # 单个订单最多成交盘口的20%  小资金放宽 大资金你给紧一点




#   分钟级别的定时函数：

# run_minutely(
#     func,          # 要运行的策略函数
#     time_rule,     # 运行频率（比如每5分钟、每10分钟）
#     reference_security
# )

# time_rule：必须用MarketTime类指定频率，比如：
# MarketTime(minute='1m')：每分钟运行一次；
# MarketTime(minute='5m')：每 5 分钟运行一次；
# MarketTime(minute='30m')：每 30 分钟运行一次。



# 实战：

# def initialize(context):# 每5分钟运行一次futures_5m_strategy函数（期货策略）
#     run_minutely(
#         futures_5m_strategy,
#         time_rule=MarketTime(minute='5m'),
#         reference_security='IF2503.CCFX'  # 参考期货标的，确定交易时段)




#macd策略
# from jqlib.technical_analysis import MACD
# MACD(security_list,check_date,SHORT, LONG,MID)

# 5日均线策略
# # 方式1：通配符导入（示例代码的写法）
#  from jqlib.technical_analysis import *
#  MA(security_list, check_date, timeperiod=5, unit='1d')  # 直接用MA，无需前缀

  
#from jqlib.technical_analysis import *
#security = '000001.XSHE'
#check_dates = ['2022-09-05'，'2022-09-06'，'2022-09-07"]

#for check_date in check_dates:
#    MA5 = MA(security,check_date=check_date,timeperiod=5)
#    MA10 = MA(security,check_date=check_date,timeperiod=10)
#    MA20 = MA(security,check_date=check_date,timeperiod=20)
#
#    print(check_date,'5日均线:',MA5[security])
#    print(check_date,'10日均线:',MA10[security])
#    print(check_date,'20日均线:',MA20[security])

#返回值是字典 所以用MA5[security] 这种方式获取 

#策略函数
def market_open(context):
    security = g.security
    #close_data = attribute_history(security, 5, '1d', ['close']) # 获取收盘价数据
    close_data = get_price(security, count=5, frequency='1d', fields=['close'])  #用get_price 代替 attribute_history 获取收盘价数据  这是新版的方法

    MA5 = close_data['close'].mean()  # 计算5日均线
    current_price = close_data['close'][-1]  # 当前价格

    cash = context.portfolio.available_cash  # 获取当前现金余额


    if current_price >  1.01*MA5:  # 当前价格高于5日均线1%
        order_value(security, cash)  # 买入全部可用现金
        log.info("买入 %s" % (security))   #打印买入日志 这是巨宽的写法

    elif current_price < MA5 and context.portfolio.positions[security].closeable_amount > 0:  # 当前价格低于5日均线1%
        #position = context.portfolio.positions[security].total_amount  # 获取当前持仓数量
        order_target(security, 0)  # 卖出全部持仓
        log.info("卖出 %s" % (security))   #打印卖出日志



    record(stock_price=current_price)  # 记录当前价格和5日均线，方便回测时绘图查看指标效果