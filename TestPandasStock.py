import matplotlib.pyplot as plt
import pandas as pd
from unittest import TestCase

class TestPandasStock:


    def ReadFile(self):
        flie_name = "./demo.csv"
        df = pd.read_csv(flie_name)
        return df


    def testReadFile(self):
        flie_name = "./demo.csv"
        df = pd.read_csv(flie_name)

        print(df.info())                    #打印 df 的 “元信息”（行列数、列名、数据类型、缺失值等）
        print("-------------------")
        print(df.describe())                #打印 df 的 “描述性统计信息”（均值、标准差、最小值、最大值等）


    #时间处理
    def testTime(self):

        df = self.ReadFile()

        df.columns = ['stock_id', 'date', 'close', 'open', 'high', 'low','volume'] # 重命名列

        df['date'] = pd.to_datetime(df['date'])  # 将 'date' 列转换为 datetime 类型

        df['year'] = df['date'].dt.year        # 提取年份
        df['month'] = df['date'].dt.month      # 提取月份

        return df



    def testCloseMin(self):
        
         df = self.testTime()   #读取文件改列名然后进行时间处理

         print("所有股票的最低收盘价是：{}".format(df['close'].min()))  #计算 'close' 列的最小值
         print("所有股票的最低价所在的行索引：{}".format(df['close'].idxmin()))  #获取 'close' 列最小值所在的行索引
         print("最低收盘价所在的完整行数据：\n{}".format(df.loc[df['close'].idxmin()]))  #获取 'close' 列最小值所在的完整行数据
         print(df.loc[0]) #输出第一行数据（其实是csv表格的第二行 因为第一行是表头）

        #先分组在计算
         print("每个股票的月平均收盘价是：{}".format(df.groupby('month')['close'].mean())) #按月份分组，计算每组的 'close' 列最小值
         print("每个股票的年平均收盘价是：{}".format(df.groupby('year')['close'].mean()))   #按年份分组，计算每组的 'close' 列最小值


    #计算涨跌幅
    def testRipples_ratio(self):
        df = self.testTime()   #读取文件改列名然后进行时间处理

        df["rise"] = df["close"].diff()  #计算收盘价的涨跌幅  和 df["close"] - df["close"].shift(1) 等级

    
        #shift(1)：向下平移 1 行（当前行取「上一行」的值）；
        #shift(-1)：向上平移 1 行（当前行取「下一行」的值）；


        df["ripples_ratio"] = df["rise"] / df["close"].shift(1)  #计算涨跌幅比例






if __name__ == "__main__":
    # 1. 实例化类
    test_obj = TestPandasStock()
    # 2. 调用testReadFile方法
    #test_obj.testReadFile()
    # 3. 调用testTime方法
    test_obj.testCloseMin()