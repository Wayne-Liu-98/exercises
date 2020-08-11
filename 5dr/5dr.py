# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 11:11:43 2020

@author: 19424
"""
import requests
import sys
import time
import pandas as pd
import numpy as np
import datetime
from dateutil.parser import parse
import argparse

# close = pd.read_hdf('G:/Innoasset/004_/ClosePriceAdj.hdf5')
# top = pd.read_hdf('G:/Innoasset/004_/Top1500.hdf5').replace(0,np.nan)
# industry = pd.read_hdf('G:/Innoasset/004_/ZXF.hdf5',key='/data')['2010-01-04':'2015-06-30']


def ret(df_close):
    df_prev_close = df_close.shift(1)
    return df_close/df_prev_close - 1

def signals(df_ret, df_top):
    sig = -sum([df_ret.shift(1), df_ret.shift(2), df_ret.shift(3), df_ret.shift(4), df_ret.shift(5)])*df_top
    sig = sig['2010-01-04':'2015-06-30']
    sig_r = 2*((sig.rank(axis = 1)-1).div((sig.count(axis=1)-1),axis=0)-0.5)   
    sig_p = (sig_r.abs()**1.5)*(np.sign(sig_r))
    return sig_p


def ind_avg_row(row_):
    
    row_df = row_.unstack()
    ind_mean = row_df.groupby(row_df['ind']).mean()
    row = pd.Series([np.NaN]*int(len(row_)/2), index=row_[:,'ind'].index, name = row_.name)
    for val in row_[:,'ind'].unique():
        #row[row[list(map(lambda x:x*2+1,range(int(len(row)/2))))][list(row[:,'ind']==val)].index.tolist()] =  ind_mean.loc[val].values[0]
        row[row_[:,'ind']==val] = ind_mean.loc[val].values[0]
    return row


def ind_avg(df_signals, df_ind):
    df_signals = df_signals.copy()
    df_signals.index = pd.MultiIndex.from_arrays([df_signals.index, ['sig']*len(df_signals.index)], names = ['date', 'type'])
    df_ind.index = pd.MultiIndex.from_arrays([df_ind.index, ['ind']*len(df_ind.index)], names = ['date', 'type'])
    ind = (df_signals.append(df_ind)).unstack()
    return ind.apply(ind_avg_row, axis=1)
    




# prev_close = close.shift(1)
# ret = close/prev_close - 1
# sig = -sum([ret.shift(1),ret.shift(2),ret.shift(3),ret.shift(4),ret.shift(5)])*top
# sig = sig['2010-01-04':'2015-06-30']
# sig_r = 2*((sig.rank(axis = 1)-1).div((sig.count(axis=1)-1),axis=0)-0.5)   
# sig_p = (sig_r.abs()**1.5)*(np.sign(sig_r))
# INDEX = sig_p.index
# sig_p.index = pd.MultiIndex.from_arrays([sig_p.index,['sig']*len(sig_p.index)],names = ['date','type'])
# industry.index = pd.MultiIndex.from_arrays([industry.index,['ind']*len(industry.index)],names = ['date','type'])
# #industry.index = ([industry.index,['ind']*len(industry.index)],names = ['a','b'])
# ind = (sig_p.append(industry)).unstack()

# def ind_avg(row):
#     na_positions = row[row==np.NaN]
#     for val in row[:,'ind'].unique():
#         row[:,'sig'][row[:,'ind']==val] = row[:,'sig'][row[:,'ind']==val].mean()
#     row[na_positions] = np.NaN
#     return row

# def ind_avg(row):
    
#     row_df=row.unstack()
#     ind_mean = row_df.groupby(row_df['ind']).mean()
#     ROW = pd.Series([np.NaN]*int(len(row)/2),index = row[:,'ind'].index,name = row.name)
#     for val in row[:,'ind'].unique():
#         #row[row[list(map(lambda x:x*2+1,range(int(len(row)/2))))][list(row[:,'ind']==val)].index.tolist()] =  ind_mean.loc[val].values[0]
#         ROW[row[:,'ind']==val] = ind_mean.loc[val].values[0]
#     return ROW

# IND = ind.apply(ind_avg,axis=1)
# sig_n=sig_p-IND
# sig_n.index = INDEX

def weight(df_ret, df_top, df_ind):
    df_signals = signals(df_ret, df_top)
    index = df_signals.index
    df_avg = ind_avg(df_signals, df_ind)
    df_avg.index = df_signals.index#index
    df_signals = df_signals - df_avg
    return df_signals.div(df_signals.abs().sum(axis=1),axis=0)


def pnl(df_weight, df_ret):
    pnl_ = (df_weight.shift(1)*df_ret['2010-01-04':'2015-06-30']).sum(axis=1)
    print ('annual return is {}'.format(pnl_.mean()*250))
    print ('annual IR is {}'.format(((pnl_.mean())/(pnl_.std()))*(250**0.5)))
    return pnl_
    

def m_d_d(pnl_):
    cum_pnl = pnl_.cumsum()
    s = pd.Series([np.NaN]*len(cum_pnl),index = cum_pnl.index)
    for i in range(len(cum_pnl)):
        s[i] = cum_pnl[i]-cum_pnl[0:i].max()
    max_draw_down = s.min()
    print ('max draw down is {}'.format(max_draw_down))


def demo():
    df_close = pd.read_hdf('G:/Innoasset/004_/ClosePriceAdj.hdf5')
    df_top = pd.read_hdf('G:/Innoasset/004_/Top1500.hdf5').replace(0,np.nan)
    df_ind = pd.read_hdf('G:/Innoasset/004_/ZXF.hdf5',key='/data')['2010-01-04':'2015-06-30']
    df_ret = ret(df_close)
    df_signals = signals(df_ret, df_top)
    df_weight = weight(df_ret, df_top, df_ind)
    pnl_ = pnl(df_weight, df_ret)
    m_d_d(pnl_)
    turnover = (df_weight - df_weight.shift(1)).abs().sum(axis=1).mean()
    print('turnover is {}'.format(turnover))
    
    
    




# weight = sig_n.div(sig_n.abs().sum(axis=1),axis=0)
# pnl = (weight.shift(1)*ret['2010-01-04':'2015-06-30']).sum(axis=1)
# Annual_ret = pnl.mean()*250
# Annual_IR =((pnl.mean())/(pnl.std()))*(250**0.5)
# cum_pnl = pnl.cumsum()
# def m_d_d(series):
#     s = pd.Series([np.NaN]*len(series),index = series.index)
#     for i in range(len(series)):
#         s[i] = series[i]-series[0:i].max()
#     return s.min()
# max_draw_down = m_d_d(cum_pnl)
# turnover = (weight - weight.shift(1)).abs().sum(axis=1).mean()

# def corr(a):
#     return pd.DataFrame([sig_n[a],ret['2010-01-04':'2015-06-30'][a]]).T.corr().values[1][0]
# df = pd.DataFrame()
# for a in list(sig.columns):
    
#     df[a] = [corr(a)] sig与ret的相关系数
# df = df.T


