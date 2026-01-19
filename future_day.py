"""
单品种期货策略：
- 20日最高点突破买多
- 20日最低点突破卖空
- 止损点：20日简单移动平均价（MA20）
- 止盈点：基于开仓价与止损价的3倍（3R）
- 全仓买入/卖空（按保证金计算最大可开手数）

基于仓位与下单示例来自工作区其它文件（future.py/5min.py）的函数用法。
"""
from jqdata import *


def initialize(context):
	# 基础设置（参考 future.py）
	set_benchmark('000300.XSHG')
	set_option('use_real_price', True)

	# 期货账户设置（使用默认子账户+保证金设置）
	set_subportfolios([SubPortfolioConfig(cash=context.portfolio.starting_cash, type='index_futures')])
	set_order_cost(OrderCost(open_commission=0.000023, close_commission=0.000023, close_today_commission=0.0023), type='index_futures')
	# 可修改为所需保证金比例
	set_option('futures_margin_rate', 0.15)
	set_slippage(StepRelatedSlippage(2))

	# 策略参数
	# 指定期货品种标的（如 'IF' 或 'IM'），改为黄金合约
	g.underlying = 'AU'
	log.info('初始化：交易标的设置为 %s' % g.underlying)
	# 计算周期
	g.window = 20

	# 状态变量
	g.contract = None
	g.position_side = None  # 'long' / 'short' / None
	g.entry_price = None
	g.stop_price = None
	g.take_profit = None

	# 在日盘撮合时段下单：把决策调度到日盘开盘后（09:01），收盘前强制平仓于 15:25
	# 避免在 initialize 时传入未初始化的 g.contract 导致 TypeError，使用已知基准作为 reference_security
	run_daily(market_open, time='09:01', reference_security='000300.XSHG')
	run_daily(after_market_close, time='15:25', reference_security='000300.XSHG')



def before_market_open(context):
	# 使用最简单可靠的主力合约选择：取 get_future_contracts(...)[0]
	try:
		res = get_future_contracts(g.underlying)
		log.info('get_future_contracts(%s) -> %s' % (g.underlying, str(res)))
		g.contract = res[0] if (res and len(res) > 0) else None
		if g.contract is None:
			log.warning('未找到主力合约：%s' % g.underlying)
		else:
			log.info('选定主力合约：%s' % g.contract)
	except Exception as e:
		log.error('获取合约失败: %s' % str(e))
		g.contract = None


def market_open(context):
	# 主逻辑：开仓、止损、止盈、全仓下单
	# 在每次做决定前获取最新主力合约，确保使用当日主力合约下单（简单逻辑）
	try:
		res = get_future_contracts(g.underlying)
		log.info('get_future_contracts(%s) -> %s' % (g.underlying, str(res)))
		g.contract = res[0] if (res and len(res) > 0) else g.contract
		if g.contract is None:
			log.warning('market_open: 未找到主力合约，跳过当日交易')
			return
	except Exception as e:
		log.error('market_open 获取合约失败: %s' % str(e))
		if g.contract is None:
			return

	log.info('market_open 使用合约: %s' % g.contract)

	# 获取历史数据（20日）
	try:
		hist = attribute_history(g.contract, g.window, '1d', ('close', 'high', 'low'))
	except Exception:
		return

	closes = hist['close']
	highs = hist['high']
	lows = hist['low']

	actual_n = len(closes)
	if actual_n < g.window:
		log.warning('历史数据天数(%s)少于设定窗口(%s)，将使用可用天数计算' % (actual_n, g.window))

	ma20 = sum(closes) / actual_n
	highest20 = max(closes)
	lowest20 = min(closes)

	# 当前价格（使用最新日收盘价）
	current_price = closes[-1]
	log.info('hist len=%s ma20=%s highest20=%s lowest20=%s current=%s' % (len(closes), ma20, highest20, lowest20, current_price))

	# 计算可开合约数量（尽量使用全部可用保证金）
	cash = context.portfolio.cash
	margin_rate = get_execute_margin_rate()
	multiplier = get_contract_multiplier(g.contract)
	if multiplier is None or multiplier <= 0 or margin_rate is None or margin_rate <= 0:
		log.warning('合约乘数或保证金比例不可用 multiplier=%s margin_rate=%s' % (multiplier, margin_rate))
		max_qty = 1
	else:
		# 使用保守的整手数计算
		try:
			max_qty = int(cash / (current_price * multiplier * margin_rate))
			if max_qty < 1:
				max_qty = 1
		except Exception:
			max_qty = 1

	# 检查持仓
	long_pos = len(context.portfolio.long_positions) > 0
	short_pos = len(context.portfolio.short_positions) > 0

	# 入场：突破20日最高点买多（无持仓时），>= 包含等于边界
	if (not long_pos) and (not short_pos) and (current_price >= highest20):
		amt = max_qty
		try:
			res_order = order(g.contract, amt, side='long')
			log.info('尝试开多: 合约=%s 手数=%s 结果=%s' % (g.contract, amt, str(res_order)))
		except Exception as e:
			log.error('开多下单失败: %s' % str(e))
		g.position_side = 'long'
		g.entry_price = current_price
		g.stop_price = ma20
		g.take_profit = g.entry_price + 3 * (g.entry_price - g.stop_price)
		log.info('开多状态记录 entry=%s stop=%s tp=%s' % (g.entry_price, g.stop_price, g.take_profit))
	else:
		if (not long_pos) and (not short_pos):
			log.info('未开多：current_price > highest20 条件不满足 (%s > %s)' % (current_price, highest20))

	# 入场：突破20日最低点卖空（无持仓时），<= 包含等于边界
	if (not long_pos) and (not short_pos) and (current_price <= lowest20):
		amt = max_qty
		try:
			res_order = order(g.contract, amt, side='short')
			log.info('尝试开空: 合约=%s 手数=%s 结果=%s' % (g.contract, amt, str(res_order)))
		except Exception as e:
			log.error('开空下单失败: %s' % str(e))
		g.position_side = 'short'
		g.entry_price = current_price
		g.stop_price = ma20
		g.take_profit = g.entry_price - 3 * (g.stop_price - g.entry_price)
		log.info('开空状态记录 entry=%s stop=%s tp=%s' % (g.entry_price, g.stop_price, g.take_profit))
	else:
		if (not long_pos) and (not short_pos):
			log.info('未开空：current_price < lowest20 条件不满足 (%s < %s)' % (current_price, lowest20))

	# 止损/止盈检查（如果有持仓）
	# 获取最新逐笔或当日价格：这里使用当日收盘价 current_price
	if long_pos or g.position_side == 'long':
		# 若跌破止损价，则全部平多
		if (g.stop_price is not None) and (current_price <= g.stop_price):
			try:
				order_target(g.contract, 0, side='long')
				log.info('多头止损 平仓 %s' % g.contract)
			except Exception as e:
				log.error('多头止损平仓失败: %s' % str(e))
			reset_position_state()
		# 若达到止盈则平仓
		elif g.take_profit is not None and current_price >= g.take_profit:
			try:
				order_target(g.contract, 0, side='long')
				log.info('多头止盈 平仓 %s' % g.contract)
			except Exception as e:
				log.error('多头止盈平仓失败: %s' % str(e))
			reset_position_state()

	if short_pos or g.position_side == 'short':
		if (g.stop_price is not None) and (current_price >= g.stop_price):
			try:
				order_target(g.contract, 0, side='short')
				log.info('空头止损 平仓 %s' % g.contract)
			except Exception as e:
				log.error('空头止损平仓失败: %s' % str(e))
			reset_position_state()
		elif g.take_profit is not None and current_price <= g.take_profit:
			try:
				order_target(g.contract, 0, side='short')
				log.info('空头止盈 平仓 %s' % g.contract)
			except Exception as e:
				log.error('空头止盈平仓失败: %s' % str(e))
			reset_position_state()


def after_market_close(context):
	# 收盘强制平仓（可根据需要注释）
	if len(context.portfolio.long_positions) > 0 or len(context.portfolio.short_positions) > 0:
		if g.contract is not None:
			order_target(g.contract, 0)
			log.info('收盘平仓 %s' % g.contract)
	reset_position_state()


def reset_position_state():
	g.position_side = None
	g.entry_price = None
	g.stop_price = None
	g.take_profit = None


def log_order_and_trades(res_order):
	# 通用的订单与成交查询日志函数，接收 order() 或 order_target() 的返回值
	try:
		log.info('订单已返回：%s' % str(res_order))
		order_id = None
		if isinstance(res_order, dict):
			order_id = res_order.get('order_id') or res_order.get('entrust_id')
		else:
			order_id = getattr(res_order, 'order_id', None) or getattr(res_order, 'entrust_id', None)

		if order_id is not None:
			try:
				o = get_order(order_id)
				t = None
				try:
					t = get_trades(order_id=order_id)
				except Exception:
					# 部分环境 get_trades 可能使用不同签名，尝试不传参数调用
					try:
						t = get_trades()
					except Exception:
						t = 'get_trades 调用失败'
				log.info('get_order(%s) -> %s' % (order_id, str(o)))
				log.info('get_trades(order_id=%s) -> %s' % (order_id, str(t)))
			except Exception as e:
				log.error('查询订单/成交失败: %s' % str(e))
	except Exception as e:
		log.error('log_order_and_trades 内部错误: %s' % str(e))


def get_execute_margin_rate():
	# 尝试读取设置的期货保证金比例
	try:
		return float(get_option('futures_margin_rate'))
	except Exception:
		# fallback to 0.15
		return 0.15


def get_contract_multiplier(symbol):
	# 尝试从合约信息中读取乘数（不同环境属性名可能不同），提供多个候选字段
	try:
		info = get_security_info(symbol)
		for attr in ('volume_multiple', 'contract_multiplier', 'unit', 'volume_multiple'):
			val = getattr(info, attr, None)
			if val:
				return float(val)
	except Exception:
		pass
	return None

