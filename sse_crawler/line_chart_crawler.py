# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 17:40:01 2020

@author: 19424
"""

import json
import requests
import pandas as pd
from log import get_my_logger
import logging
import os

#爬取程序
class ChartCrrawler:
    def __init__(self):
        self.url = 'http://yunhq.sse.com.cn:32041//v1/sh1/line/000001?callback=jQuery11240035099302531294896_1596448208138&begin=0&end=-1&select=time%2Cprice%2Cvolume&_=1596448208141'
        response = requests.get(self.url,headers={'Referer': 'http://www.sse.com.cn/market/price/trends/'})
        json_str = response.text[44:-1]
        data = json.loads(json_str)
        self.line = data['line']
        self.df = pd.DataFrame(self.line)
        self.df.columns = ['Time', 'Price', 'Amount']
        self.logger = get_my_logger([['chart_info.log', logging.INFO],
                             ['chart_warning.log', logging.WARNING],
                             ['chart_error.log', logging.ERROR]])
        self.path = './output_chart'
    

    def save_csv(self):
        folder = os.path.exists(self.path)
        if not folder:
            os.makedirs(self.path)
            self.logger.info('new folder created for saving data.')
        self.df.to_csv(self.path+'//chart_data.csv', index=False)


if __name__=='__main__':
    ChartCrrawler().save_csv()