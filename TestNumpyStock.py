import numpy as np



class TsetNumpyStock(TestCase):
    """读取指定列
        numpy.loadtxt需要传入4个关键字参数:
        1.fname是文件名，数据类型为字符串str:
        2.delimiter是分隔符，数据类型为字符str;
        3.usecols是读取的列数，数据类型为元组tuple，其中元素个数有多少个，则选出多少列:
        4.unpack是是否解包，数据类型为布尔bo0l.
    #"""

    def testReadFile(self):
        file_name = "./demo.csv"

        #获取收盘价 和 成交量  这样获得是end_price 和 volumn两个数组
        end_price,volumn = np.loadtxt(
            fname= file_name,
            delattr= ",",
            usecols= (2,6), #第三列 和 第七列
            unpack= True
        ) 



    #计算最大最小值
    def testMaxAndMin(self):
        file_name = "./demo.csv"

        #获取最高价 和 最低价  这样获得是end_price 和 volumn两个数组
        high_price,low_price = np.loadtxt(
            fname= file_name,
            delattr= ",",
            usecols= (4,5), #第四列 和 第五列
            unpack= True
        ) 

        print("max_price = {}".format(high_price.max()))  #那取最高价就是 high_price数组内的max喽
        print("max_price = {}".format(low_price.min())) 



    def testPtp(self):
        file_name = "./demo.csv"

        high_price,low_price = np.loadtxt(
            fname= file_name,
            delattr= ",",
            usecols= (4,5), #第四列 和 第五列
            unpack= True
        ) 

        print("max_min_of_high_price = {}".format(np.ptp(high_price)))    #算最高价的 极差  这有什么意义？  可以算某个时间段比如收盘价的max-min   
        print("max_min_of_high_price = {}".format(np.ptp(low_price))) 



    #计算成交量加权平均价格 VWAP 
    def testAve(self):
        file_name = "./demo.csv"

        end_price,volumn = np.loadtxt(
            fname= file_name,
            delattr= ",",
            usecols= (2,6), #第二列 和 第列列
            unpack= True
        ) 
        print("avg_price = {}".format(np.average(end_price)))  #平均价格
        print("avg_price = {}".format(np.average(end_price,weighr = volumn)))  #加权平均价格


    #计算中位数
    def testMed(self):
        file_name = "./demo.csv"

        end_price,volumn = np.loadtxt(
            fname= file_name,
            delattr= ",",
            usecols= (2,6), #第二列 和 第列列
            unpack= True
        ) 
        print("avg_price = {}".format(np.median(end_price)))  #收盘价中位数
       

    #计算方差
    def testVar(self):
        file_name = "./demo.csv"

        end_price,volumn = np.loadtxt(
            fname= file_name,
            delattr= ",",
            usecols= (2,6), #第二列 和 第列列
            unpack= True
        ) 
        print("avg_price = {}".format(np.var(end_price)))  #收盘价方差


    
    #计算 日对数收益率 再算日波动率  再算年波动率
    def testVolatility(self):
        file_name = "./demo.csv"

        end_price,volumn = np.loadtxt(
            fname= file_name,
            delattr= ",",
            usecols= (2,6), #第二列 和 第列列
            unpack= True
        ) 

        #计算对数收益率
        log_returns = np.diff(np.log(end_price))

        #计算日波动率（对数收益率的样本标准差） 
        # 仍用ddof=1（样本标准差），贴合“用历史数据估计未来波动率”的场景
        daily_volatility = np.std(log_returns, ddof=1)

        # ===================== 第四步：计算年化波动率 =====================
        annualization_factor = np.sqrt(255)  # A股年交易天数≈255
        annual_volatility = daily_volatility * annualization_factor

        return log_returns,daily_volatility,annual_volatility
    

#关于波动率：- 波动率看的是「收益率的离散程度」：只要收益率稳定（哪怕持续涨 / 持续跌），波动率就低；
#- 哪怕价格最终没涨没跌，但只要中途涨跌反复，收益率的离散程度就高，波动率就高



#均线可以通过滑动窗口平混函数求   也可以用卷积  但是卷积的的化实战中用的少 因为不够直观
# 2. 定义滑动窗口平均函数（通用计算N日均线）
    def calc_ma(self,price_arr, window):
        # 生成滑动窗口：shape=(len(price_arr)-window+1, window)
        sliding_windows = np.lib.stride_tricks.sliding_window_view(price_arr, window)
        # 对每个窗口求均值（即均线）
        ma = np.mean(sliding_windows, axis=1)
        # 补全前window-1个NaN（因为前window-1天不够算均线）
        ma_full = np.concatenate([np.full(window-1, np.nan), ma])
        return ma_full
    

    def get_5(self):
        file_name = "./demo.csv"

        end_price,volumn = np.loadtxt(
            fname= file_name,
            delattr= ",",
            usecols= (2,6), #第二列 和 第列列
            unpack= True
        ) 

        return self.calc_ma(end_price,5)
    


    