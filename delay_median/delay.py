# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 16:15:44 2020

@author: user
"""

import os
import pandas as pd


def file_list(filepath):
    files = os.listdir(filepath)
    files = [*map(lambda x: (filepath+x), files)]
    return files


def find_col(df, name):
    # find the position of desired column regardless of the index in the front
    return df.filter(regex=(".*]{}".format(name))).columns.values[0]


def delay(df):
    return df[find_col(df, 'LocalTime')] - df[find_col(df, 'TradingTime')].astype(int)


def single_file(file, files):
    df = pd.read_csv(file, sep='|', converters = {u'[3]TradingTime':str})
    df['delay'] =  delay(df)
    df['minute'] = df['[3]TradingTime'].apply(lambda t: t[:4])
    df.rename(columns={find_col(df, 'Exg'): 'exg'}, inplace=True)
    df = df[['minute', 'exg', 'delay']]
    if files.index(file) % 100 == 0:
        print('{} out of {} has been completed'.format(files.index(file), len(files)))
    return df


def demo(filepath='G:/Innoasset/01_delay/data/orderbook/'):
    files = file_list(filepath)
    date = files[0][-12:-4]
    df = pd.concat([single_file(file, files) for file in files])
    df.delay = df.delay.astype(int)
    result = df.groupby([df['minute'], df['exg']]).median().unstack()
    result.columns = ['SSE','SZSE']
    result.to_csv("{}.csv".format(date), index=True)


if __name__=="__main__":
    demo()