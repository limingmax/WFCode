# @Time   : 2018-10-23
# @Author : zxh
from zutils.zrpc.server.threadpool_server import ThreadpoolServer, map_handle
from zutils.logger import Logger
import pandas as pd
import numpy as np
import math
# import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import acf,pacf,plot_acf,plot_pacf
from statsmodels.tsa.arima_model import ARMA
import happybase

import json
import cgi
import socketserver

import configparser
cf = configparser.ConfigParser()
cf.read("python.ini")
hbase_host = cf.get("hbase", "host")
hbase_port = cf.getint("hbase", "port")
register_address=cf.get("register","address")


# 创建服务，单例，如果资源有竞争，创建放在func里
@map_handle('/trend', 'handle1', 10)
class ExampleSvr():
    def select(self,metric, resource, year, month, day,namespace):
        print("===start===")
        #base_host = hbase_host
        #hbase_port = hbase_port
        print(hbase_port)
        print(hbase_host)
        connection = happybase.Connection(hbase_host, hbase_port)
        print("===end===")
        # connection = testHTTPServer_RequestHandler.connection
        t = connection.table('Monitor_record')
        last = 0
        result_list = []
        print("namespace",namespace)
        if(namespace):
            year, month, day = self.time_handle(year, month, day)
            year, month, day = self.time_handle(year, month, day)
            filter1 = bytes(
                "SingleColumnValueFilter ('Metric', 'resourceName', =, 'binary:{resource}') AND SingleColumnValueFilter ('Metric', 'index_name', =, 'binary:{metric}') AND SingleColumnValueFilter ('Metric', 'time', =, 'regexstring:{year}-{month}-.*T.*:00:00') AND SingleColumnValueFilter ('Metric', 'type', =, 'binary:pod')AND SingleColumnValueFilter ('Metric', 'namespace_name', =, 'binary:{namespace}')".format(
                    resource=resource, metric=metric, year=year, month=month,namespace=namespace), encoding='utf-8')
            result = t.scan(filter=filter1,row_start=bytes('{year}-{month}-{day}'.format(year=year,month=month,day=day),encoding='utf-8'))
            list1=[]

            for k, v in result:
                print(k,v)
                list1.append(float(v[b'Metric:index_value'].decode()))
                last = k
                # print(last)

            # year, month, day = self.time_handle(year, month, day)
            # filter2 = bytes(
            #     " SingleColumnValueFilter ('Metric', 'resourceName', =, 'binary:{resource}') AND SingleColumnValueFilter ('Metric', 'index_name', =, 'binary:{metric}') AND SingleColumnValueFilter ('Metric', 'time', =, 'regexstring:{year}-{month}-{day}T.*:00:00')AND SingleColumnValueFilter ('Metric', 'type', =, 'binary:pod')AND SingleColumnValueFilter ('Metric', 'namespace_name', =, 'binary:{namespace}') ".format(
            #         resource=resource, metric=metric, year=year, day=day, month=month,namespace=namespace), encoding='utf-8')
            # result = t.scan(filter=filter2,row_prefix=bytes('{year}-{month}-{day}'.format(year=year,month=month,day=day),encoding='utf-8'))
            # list2=[]
            # for k, v in result:
            #     print(k, v)
            #     list2.append(float(v[b'Metric:index_value'].decode()))
            # year, month, day = self.time_handle(year, month, day)
            # filter3 = bytes(
            #     " SingleColumnValueFilter ('Metric', 'resourceName', =, 'binary:{resource}') AND SingleColumnValueFilter ('Metric', 'index_name', =, 'binary:{metric}') AND SingleColumnValueFilter ('Metric', 'time', =, 'regexstring:{year}-{month}-{day}T.*:00:00')AND SingleColumnValueFilter ('Metric', 'type', =, 'binary:pod')AND SingleColumnValueFilter ('Metric', 'namespace_name', =, 'binary:{namespace}') ".format(
            #         resource=resource, metric=metric, year=year, day=day, month=month, namespace=namespace),
            #     encoding='utf-8')
            # print(33333333)
            # result = t.scan(filter=filter3,
            #                 row_prefix=bytes('{year}-{month}-{day}'.format(year=year, month=month, day=day),
            #                                  encoding='utf-8'))
            # list3=[]
            # for k, v in result:
            #     print(k, v)
            #     list3.append(float(v[b'Metric:index_value'].decode()))
            # print(list1,"1",list2,"2",list3,"3")
            result_list =  list1
        else:
            year, month, day = self.time_handle(year, month, day)
            year, month, day = self.time_handle(year, month, day)

            filter1 = bytes(
                "SingleColumnValueFilter ('Metric', 'resourceName', =, 'binary:{resource}') AND SingleColumnValueFilter ('Metric', 'index_name', =, 'binary:{metric}') AND SingleColumnValueFilter ('Metric', 'time', =, 'regexstring:{year}-{month}-.*T.*:00:00')AND SingleColumnValueFilter ('Metric', 'type', =, 'binary:node') ".format(
                    resource=resource, metric=metric, year=year, month=month), encoding='utf-8')
            result = t.scan(filter=filter1,
                            row_start=bytes('{year}-{month}-{day}'.format(year=year, month=month, day=day),
                                             encoding='utf-8'))
            list1 = []
            for k, v in result:
                print(k,v)
                list1.append(float(v[b'Metric:index_value'].decode()))
                last = k
                # print(last)
            # year, month, day = self.time_handle(year, month, day)
            # filter2 = bytes(
            #     " SingleColumnValueFilter ('Metric', 'resourceName', =, 'binary:{resource}') AND SingleColumnValueFilter ('Metric', 'index_name', =, 'binary:{metric}') AND SingleColumnValueFilter ('Metric', 'time', =, 'regexstring:{year}-{month}-{day}T.*:00:00') AND SingleColumnValueFilter ('Metric', 'type', =, 'binary:node')".format(
            #         resource=resource, metric=metric, year=year, day=day, month=month), encoding='utf-8')
            # result = t.scan(filter=filter2,
            #                 row_prefix=bytes('{year}-{month}-{day}'.format(year=year, month=month, day=day),
            #                                  encoding='utf-8'))
            # list2=[]
            # for k, v in result:
            #     print(k, v)
            #     list2.append(float(v[b'Metric:index_value'].decode()))
            #
            # year, month, day = self.time_handle(year, month, day)
            # print(33333333)
            #
            # filter3 = bytes(
            #     " SingleColumnValueFilter ('Metric', 'resourceName', =, 'binary:{resource}') AND SingleColumnValueFilter ('Metric', 'index_name', =, 'binary:{metric}') AND SingleColumnValueFilter ('Metric', 'time', =, 'regexstring:{year}-{month}-{day}T.*:00:00')AND SingleColumnValueFilter ('Metric', 'type', =, 'binary:pod')AND SingleColumnValueFilter ('Metric', 'namespace_name', =, 'binary:{namespace}') ".format(
            #         resource=resource, metric=metric, year=year, day=day, month=month, namespace=namespace),
            #     encoding='utf-8')
            # result = t.scan(filter=filter3,
            #                 row_prefix=bytes('{year}-{month}-{day}'.format(year=year, month=month, day=day),
            #                                  encoding='utf-8'))
            # print(result)
            # list3=[]
            # print(33333333)
            #
            # for k, v in result:
            #     print(k, v)
            #     list3.append(float(v[b'Metric:index_value'].decode()))
            # print(list1, "1", list2, "2", list3, "3")
            result_list=list1
        print(result_list)
        if not result_list:
            raise  Exception("缺少目标容器节点近期数据")
        if not last:
            raise  Exception("未发现startTime当天之前的数据")
        return result_list, last.decode()

    def time_handle(self,year, month, day):
        year = int(year)
        month = int(month)
        day = int(day)

        if (day > 1):
            day = day - 1

        else:
            if (month > 1):
                month = month - 1
                if (month in [1, 3, 5, 7, 8, 10, 12]):
                    day = 31
                elif (month in [4, 6, 9, 11]):
                    day = 30
                elif year % 400 == 0 or year % 4 == 0 and year % 100 != 0:
                    day = 29
                else:
                    day = 28
            else:
                year = year - 1
                month = 12
                day = 31
        if (month >= 10):
            month = str(month)
        else:
            month = '0' + month
        if (day >= 10):
            day = str(day)
        else:
            day = '0' + str(day)
        year=str(year)
        return year, month, day

    def raw_key_time(self,b):

        c = b.split('Z')[0]
        year, month, time = c.split('-')
        day, time = time.split('T')
        hour = time.split(":")[0]
        return year, month, day, hour
    def countTime(self,time1,time2):
        year1,month1,day1,hour1=self.raw_key_time(time1)
        year2,month2,day2,hour2=self.raw_key_time(time2)
        hour1=int(hour1)
        hour2=int(hour2)
        day1=int(day1)
        day2=int(day2)
        return (day1-day2)*24+hour1-hour2+1
    def pre(self,rowlist, day):
        # rowlist=[151.0, 188.46, 199.38, 219.75, 241.55, 262.58, 328.22, 396.26, 442.04, 517.77, 626.52, 717.08, 824.38, 913.38, 1088.39, 1325.83, 1700.92, 2109.38, 2499.77, 2856.47, 3114.02, 3229.29, 3545.39, 3880.53, 4212.82, 4757.45, 5633.24, 6590.19, 7617.47, 9333.4, 11328.92, 12961.1, 15967.61]
        length = len(rowlist)
        print("length",length)
        print("day",day)
        time_series = pd.Series(rowlist)
        time_series.index = pd.Index(sm.tsa.datetools.dates_from_range('1900', str(1900 + length - 1)))
        # time_series.plot(figsize=(12,8))
        # plt.show()
        t = sm.tsa.stattools.adfuller(time_series, )
        # output=pd.DataFrame(index=['Test Statistic Value', "p-value", "Lags Used", "Number of Observations Used","Critical Value(1%)","Critical Value(5%)","Critical Value(10%)"],columns=['value'])
        # output['value']['Test Statistic Value'] = t[0]
        # output['value']['p-value'] = t[1]
        # output['value']['Lags Used'] = t[2]
        # output['value']['Number of Observations Used'] = t[3]
        # output['value']['Critical Value(1%)'] = t[4]['1%']
        # output['value']['Critical Value(5%)'] = t[4]['5%']
        # output['value']['Critical Value(10%)'] = t[4]['10%']
        # print(output)
        tlog = False
        tds = 0
        if (t[1] > 0.1):
            tlog = True
            time_series = np.log(time_series)
            tl = time_series
            # print(time_series)
        # time_series.plot(figsize=(8,6))
        # plt.show()
        # 一阶差分
        tdff = False
        t = sm.tsa.stattools.adfuller(time_series, )
        if (t[1] > 0.05):
            tdff = True
            time_series = time_series.diff(1)
        print("tlog", tlog)
        print("td", tdff)
        # 去掉空值,差分后首项为0
        time_series = time_series.dropna(how=any)
        #再看看
        t = sm.tsa.stattools.adfuller(time_series, )
        print("最后是否平稳",t[1])
        tds = time_series
        # time_series.plot(figsize=(8,6))
        # plt.show()
        # t=sm.tsa.stattools.adfuller(time_series)
        # output=pd.DataFrame(index=['Test Statistic Value', "p-value", "Lags Used", "Number of Observations Used","Critical Value(1%)","Critical Value(5%)","Critical Value(10%)"],columns=['value'])
        # output['value']['Test Statistic Value'] = t[0]
        # output['value']['p-value'] = t[1]
        # output['value']['Lags Used'] = t[2]
        # output['value']['Number of Observations Used'] = t[3]
        # output['value']['Critical Value(1%)'] = t[4]['1%']
        # output['value']['Critical Value(5%)'] = t[4]['5%']
        # output['value']['Critical Value(10%)'] = t[4]['10%']
        # print(output)
        (p, q) = (sm.tsa.arma_order_select_ic(time_series, max_ar=3, max_ma=3, ic='aic')['aic_min_order'])
        # 这里需要设定自动取阶的 p和q 的最大值，即函数里面的max_ar,和max_ma。ic 参数表示选用的选取标准，这里设置的为aic,当然也可以用bic。然后函数会算出每个 p和q 组合(这里是(0,0)~(3,3)的AIC的值，取其中最小的,这里的结果是(p=0,q=1)。
        print(p, q)
        arma_model = sm.tsa.ARMA(time_series, (p, q)).fit(disp=-1, maxiter=100)
        # 这里start要比前面1978多1，不然会报错,因为差分过了，数据少1
        predict_data = arma_model.predict(start=str(1901), end=str(1900 + length - 1 + day), dynamic=False)
        # print(predict_data)
        # print(type(predict_data))
        # print(len(predict_data))
        prelist = predict_data
        if (tdff):
            prelist = []
            # prelist.append(rowlist[0])
            if (tlog):
                for i in range(len(rowlist)):
                    # print(i)
                    prelist.append(math.exp(predict_data[i] + tl[i]))
                i = 0
                while i < day:
                    # print(i)
                    # print(predict_data[-day + i])
                    b = math.log(prelist[-1]) + predict_data[-day + i]
                    # print(b)
                    a = math.exp(b)
                    prelist.append(a)
                    # print(prelist)
                    i = i + 1
            else:
                for i in range(len(rowlist)):
                    prelist.append(rowlist[i] + predict_data[i])
                i = 0
                while i < day:

                    # print(predict_data[-day + i])
                    prelist.append(prelist[-1] + predict_data[-(day - i)])
                    # print(prelist)
                    i = i + 1
        # print(prelist)
        prelist=list(prelist)
        prelist=['%.2f' % a for a in prelist]
        print(prelist)
        return prelist
    def handle1(self, task):
        print(task)

        # data = self.rfile.read(int(self.headers['content-length']))
        # record = task["data"]
        record = task
        deviceName=record["deviceName"].split("_")


        # form = cgi.FieldStorage(
        #     fp=self.rfile,
        #     headers=self.headers,
        #     environ={'REQUEST_METHOD': 'POST',
        #              'CONTENT_TYPE': self.headers['Content-Type'],
        #              })
        #
        # deviceName=form["deviceName"].value.split("_")
        namespace=0
        if len(deviceName)==4:
            namespace=deviceName[-2]
        deviceName=deviceName[-1]
        if not deviceName:
            raise  Exception("deviceName 不能为空")
        metric=record["metric"]
        if not metric:
            raise  Exception("metric 不能为空")

        startTime=record["startTime"]
        if not startTime:
            raise Exception("startTime 不能为空")
        endTime=record["endTime"]
        if not endTime:
            raise Exception("endTime 不能为空")
        # metric=form["metric"].value
        # startTime=form["startTime"].value
        # endTime=form["endTime"].value
        year,month,day,hour=self.raw_key_time(startTime)


        result, time = self.select(metric, deviceName, year, month, day,namespace)

        q=self.countTime(endTime,time)
        if q<0:
            raise Exception("endTime应比历史数据晚")
        qq=self.countTime(endTime,startTime)
        if qq<0:
            raise Exception("endTime应比startTime晚")
        timere=[]
        hour=int(hour)+8
        for i in range(qq):
            hour=(hour+1)%24
            timere.append(hour)

        result=self.pre(result, q)

        result=result[-qq:]
        # self.send_response(200)
        # self.send_header('Content-type', 'application/json')
        # self.end_headers()
        res={
            "deviceName":record["deviceName"],
            "metric":metric,
            "time":timere,
            "value":result
        }
        # print(res)
        # a=json.dumps(res)
        return res




logger = Logger(Logger.INFO, 'example', True)
# 参数：日志级别   日志文件名   日志是否控制台输出


server = ThreadpoolServer(register_address, [ExampleSvr], logger, 'JSON',30,30, 1)
#          消息系统地址    服务列表     日志     交互协议    线程数量

server.start()




