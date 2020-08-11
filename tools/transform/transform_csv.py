# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 10:15:54 2020

@author: 19424
"""
import pandas as pd
from pandas import DataFrame


def transform(file_path='./input.csv'):
    df = pd.read_csv(file_path, sep='|', index_col = 'TradeDate')
    df = df.stack().reset_index()
    df.columns = ['TradeDate', 'SecuCode', 'ClosePrice']
    return df

