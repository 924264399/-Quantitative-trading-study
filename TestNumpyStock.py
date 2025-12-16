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
        end_price,volumn = np.loadtxt(
            fname= file_name,
            delattr= ",",
            usecols= (2,6), #第三列 到 第七列
            unpack= True
        )



    #计算最大最小值
    def testMaxAndMin(self):
        