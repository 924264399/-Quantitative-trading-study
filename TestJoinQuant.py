
def initialize(context):
    g.security = "000001.XSHE"  # 平安银行
    run.daily(market_open,time = 'every_day')  # 每个bar都执行一次handle_data函数

    set_benchmark('000300.XSHG')  # 以沪深300指数为基准
    set_option('use_real_price', True) # 使用真实价格交易

    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')  # 设置交易费用
    set_slippage(PriceSlippage(percent=0.002), type='stock') # 设置滑点
    set_option('order_volume_ratio', 0.2)  # 单个订单最多成交盘口的20%  小资金放宽 大资金你给紧一点


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