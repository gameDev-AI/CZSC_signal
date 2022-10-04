#! /usr/bin/env python
# -*- coding: utf-8 -*-

import baostock as bs
import pandas as pd
import pymysql
import time
import datetime
import calendar
from datetime import timedelta
from itertools import chain
import os
import pandas as pd
import numpy as np
from collections import OrderedDict
from czsc import CZSC, CzscAdvancedTrader, Freq
from czsc.utils import BarGenerator
from czsc import signals
from czsc.objects import RawBar
from czsc.enum import Freq
from czsc import signals
from czsc.signals.signals import get_default_signals, get_s_three_bi, get_s_d0_bi
from czsc.signals.ta import get_s_single_k, get_s_three_k, get_s_sma, get_s_macd
from czsc.signals.bxt import get_s_like_bs, get_s_d0_bi, get_s_bi_status, get_s_di_bi, get_s_base_xt, get_s_three_bi

from czsc.utils.ta import SMA, EMA, MACD, KDJ

import new_signal

import sys
from czsc.utils.cache import home_path
from czsc import signals
from czsc.objects import Freq, Operate, Signal, Factor, Event
from collections import OrderedDict
from czsc.traders import CzscAdvancedTrader
from czsc.objects import PositionLong, PositionShort, RawBar


from ts_fast_backtest import dc
from czsc.data import freq_cn2ts
from czsc.utils import BarGenerator
from czsc.traders.utils import trade_replay


os.environ['czsc_verbose'] = "1"        # 是否输出详细执行信息，0 不输出，1 输出
os.environ['czsc_min_bi_len'] = "6"     # 通过环境变量设定最小笔长度，6 对应新笔定义，7 对应老笔定义
pd.set_option('mode.chained_assignment', None)
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 20)

freq_map = {'1min': Freq.F1, '5min': Freq.F5, '15min': Freq.F15, '30min': Freq.F30,
            '60min': Freq.F60, 'D': Freq.D, 'W': Freq.W, 'M': Freq.M}

def float2(value, num):
    #print(round(float(value),num))
    return round(float(value),num)
    
    
def download_day_data_by_code(freq, code, start_date, end_date):
    # 获取指定股票数据
    data_df = pd.DataFrame()
    #print(stockcodes.shape[0])
    if True:
    # for code in stockcodes["code"]:
        print("Downloading day:" + code)
        # k_rs = bs.query_history_k_data_plus("sz.003037", "date,time,code,open,high,low,close,volume,amount,adjustflag", start_date, end_date, frequency="30", adjustflag="3")
        k_rs = bs.query_history_k_data_plus(code, "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST", start_date, end_date, frequency="d", adjustflag="2")
        ##sh.600006
        # k_rs = bs.query_history_k_data_plus("sh.600006", "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST", start_date, end_date, frequency="d", adjustflag="2")
        df_stockload = k_rs.get_data()
        c_len = df_stockload.shape[0]
        freq = 'D'
        bars = []
        if c_len > 0:
            # print(df_stockload['close'][c_len - 1])
            for j in range(c_len):
                #print(df_stockload['amount'][j])
                try:
                    bars.append(RawBar(symbol=df_stockload['code'][j], dt=pd.to_datetime(df_stockload['date'][j]), id=j, freq=freq_map[freq],
                                   open=round(float(df_stockload['open'][j]), 2),
                                   close=round(float(df_stockload['close'][j]), 2),
                                   high=round(float(df_stockload['high'][j]), 2),
                                   low=round(float(df_stockload['low'][j]), 2),
                                   vol=round(float(df_stockload['volume'][j]), 2)))
                except Exception as err:
                     print(err)
                     bars = []
                    #print(str(resu[0]),str(resu[1]))
                     return bars
            #print(c_len)
            return bars
        else:
            return bars
            
def download_30_data_by_code(freq, code, start_date, end_date):
    data_df = pd.DataFrame()
    #print(stockcodes.shape[0])
    if True:
    # for code in stockcodes["code"]:
        print("Downloading 30min:" + code)
        # k_rs = bs.query_history_k_data_plus("sz.003037", "date,time,code,open,high,low,close,volume,amount,adjustflag", start_date, end_date, frequency="30", adjustflag="3")
        k_rs = bs.query_history_k_data_plus(code, "date,time,code,open,high,low,close,volume,amount,adjustflag", start_date, end_date, frequency="30", adjustflag="2")
        ##sh.600006
        # k_rs = bs.query_history_k_data_plus("sh.600006", "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST", start_date, end_date, frequency="d", adjustflag="2")
        df_stockload = k_rs.get_data()
        c_len = df_stockload.shape[0]
        freq = '30min'
        bars = []
        if c_len > 0:
            #print(df_stockload)
            # print(df_stockload['close'][c_len - 1])
            for j in range(c_len):
                #print(df_stockload['amount'][j])
                try:
                    str = df_stockload['time'][j]
                    dt = datetime.datetime.strptime(str, "%Y%m%d%H%M%S%f")
                    bars.append(RawBar(symbol=df_stockload['code'][j], dt=dt, id=j, freq=freq_map[freq],
                                   open=round(float(df_stockload['open'][j]), 2),
                                   close=round(float(df_stockload['close'][j]), 2),
                                   high=round(float(df_stockload['high'][j]), 2),
                                   low=round(float(df_stockload['low'][j]), 2),
                                   vol=round(float(df_stockload['volume'][j]), 2)))
                except Exception as err:
                     print(err)
                     bars = []
                    #print(str(resu[0]),str(resu[1]))
                     return bars
            #print(c_len)
            return bars
        else:
            return bars

    
def get_all_stock(date):
    stock_rs = bs.query_all_stock(date)
    stock_df = stock_rs.get_data()
    #print(stock_df)
    return stock_df
    

                    
def get_last_trade_day(start_dt, end_dt):
    rs = bs.query_trade_dates(start_date=start_dt, end_date=end_dt)
    print('query_trade_dates respond error_code:'+rs.error_code)
    print('query_trade_dates respond  error_msg:'+rs.error_msg)

    #### 打印结果集 ####
    data_list = []


    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data = rs.get_row_data()
        #print(data[1])
        if data[1] == '1':
            data_list.append(data)
        
    #result = pd.DataFrame(data_list, columns=rs.fields)

    #### 结果集输出到csv文件 ####   
    #result.to_csv("D:\\trade_datas.csv", encoding="gbk", index=False)
    #print(data_list)
    print(data_list[len(data_list) - 1][0])
    return data_list[len(data_list) - 1][0]
    

def get_delta_day():
        start_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '8:00', '%Y-%m-%d%H:%M')
        end_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '18:00', '%Y-%m-%d%H:%M')
        # 结束时间
        now_time = datetime.datetime.now()
        # 判断当前时间是否在范围时间内
        if start_time < now_time < end_time:
            return 1
        else:
            return 1
            
            
          
def trader_strategy_a(symbol):
    """A股市场择时策略A"""
    def get_signals(cat: CzscAdvancedTrader) -> OrderedDict:
        s = OrderedDict({"symbol": cat.symbol, "dt": cat.end_dt, "close": cat.latest_price})
        s.update(signals.pos.get_s_long01(cat, th=100))
        s.update(signals.pos.get_s_long02(cat, th=100))
        s.update(signals.pos.get_s_long05(cat, span='月', th=500))
        for _, c in cat.kas.items():
            if c.freq in [Freq.F30]:
                s.update(new_signal.get_s_sma(c))
                s.update(signals.other.get_s_zdt(c, di=1))
                
                s.update(new_signal.get_s_three_k(c, 1))
                s.update(new_signal.get_s_base_xt(c, di=1))
                s.update(new_signal.get_s_three_bi(c, di=1))
                s.update(new_signal.get_s_like_bs(c, di=1))
            
                s.update(signals.other.get_s_op_time_span(c, op='开多', time_span=('10:00', '14:50')))
                s.update(signals.other.get_s_op_time_span(c, op='平多', time_span=('09:35', '14:50')))

            if c.freq in [Freq.D, Freq.W]:
                s.update(new_signal.get_s_three_k(c, 1))
                s.update(new_signal.get_s_base_xt(c, di=1))
                s.update(new_signal.get_s_three_bi(c, di=1))
                s.update(new_signal.get_s_like_bs(c, di=1))
        return s

    # 定义多头持仓对象和交易事件
    long_pos = PositionLong(symbol, hold_long_a=1, hold_long_b=1, hold_long_c=1,
                            T0=False, long_min_interval=3600*4)
    long_events = [
        Event(name="开多", operate=Operate.LO, factors=[
            Factor(name="低吸", signals_all=[
                Signal("开多时间范围_10:00_14:50_是_任意_任意_0"),
                Signal("30分钟_倒1K_ZDT_非涨跌停_任意_任意_0"),
                Signal("30分钟_倒1K_均线多空_多头_任意_任意_0"),
                
                
                
            ],
            signals_any = [
                
                Signal("日线_倒1笔_三笔形态_向下奔走型_任意_任意_0"),
                Signal("30分钟_倒1笔_三笔形态_向下盘背_任意_任意_0"),
                
            ],
            signals_not = [

            ]),
            
            
            
        ]),

        Event(name="平多", operate=Operate.LE, factors=[
            Factor(name="持有资金", signals_all=[
                Signal("平多时间范围_09:35_14:50_是_任意_任意_0"),
                #Signal("30分钟_倒1K_ZDT_非涨跌停_任意_任意_0"),
                Signal("30分钟_倒1K_三K形态_顶分型_任意_任意_0"),
                
            ], signals_not=[
                
            ],
            signals_any = [
                
            ]),
            
        ]),
    ]

    tactic = {
        "base_freq": '30分钟',
        "freqs": ['日线', '周线'],
        "get_signals": get_signals,
        "signals_n": 0,

        "long_pos": long_pos,
        "long_events": long_events,

        # 空头策略不进行定义，也就是不做空头交易
        "short_pos": None,
        "short_events": None,
    }

    return tactic
    



if __name__ == '__main__':
    if True:
        time_temp = datetime.datetime.now() - datetime.timedelta(days=2000)
        start_dt = time_temp.strftime('%Y-%m-%d')
        
        day = get_delta_day()
        time_temp = datetime.datetime.now() - datetime.timedelta(days=day)
        end_dt = time_temp.strftime('%Y-%m-%d')
        
        
        bs.login()
        
        lasttradeday = get_last_trade_day(start_dt, end_dt)
        weekday = datetime.datetime.now().isoweekday()
        
        
        # 获取全部股票的信息
        all_stock_codes = get_all_stock(lasttradeday)
        # print(all_stock_codes)
        
        total = all_stock_codes.shape[0]
        # 获取全部股票的日信息
        if total != 0:
            print("获取全部股票的日信息")
            export_signals = []           
            #code = "sz.300879"
            print(sys.argv[1])
            
            code = sys.argv[1]
            
            tactic = trader_strategy_a(code)
            base_freq = tactic['base_freq']
            
            freq = 30
            
            bars = []
            bars = download_30_data_by_code(freq, code, start_dt, end_dt)
                
                
            #print(bars)
            if bars == []:
                print("k bar null") 
            else:
                bg = BarGenerator(base_freq, freqs=tactic['freqs'])
                bars1 = bars[:2000]
                bars2 = bars[2000:]
                for bar in bars1:
                    bg.update(bar)
                res_path = home_path
                trade_replay(bg, bars2, trader_strategy_a, res_path)
            
                
            
        print("handle finish")
        
