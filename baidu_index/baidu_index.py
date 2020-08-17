# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 17:42:16 2020

@author: Wayne Liu
"""
import sys
import json
import time
import copy
import random
import logging
import argparse
import datetime
import requests
import line_profiler
import numpy as np
import pandas as pd
from log import get_my_logger
from selenium import webdriver
from dateutil.parser import parse


class Cookies:
    __driver = None
    
    # Get cookies from the driver and sav it to a json file.
    @staticmethod
    def save_cookie():
        cookies = Cookies.__driver.get_cookies()
        json_cookies = json.dumps(cookies)
        with open('G:/Innoasset/003_First_Trial_Web_Scraping/cookies.json', 'w') as f:
            f.write(json_cookies)
    
    
    # Add cookies in the json to the driver to login.
    @staticmethod
    def add_cookie():
        Cookies.__driver.delete_all_cookies()
        with open('G:/Innoasset/003_First_Trial_Web_Scraping/cookies.json', 'r',
                  encoding='utf-8') as f:   
            list_cookies = json.loads(f.read())
        for i in list_cookies:
            Cookies.__driver.add_cookie(i)
    
    # First login in with old cookies and then update to new cookies.
    # Then save it and translate into desired form.
    @classmethod
    def get_cookies(cls):
        cls.__driver = webdriver.Chrome()
        cls.__driver.get("http://zhishu.baidu.com/")
        cls.add_cookie()
        cls.__driver.get("http://zhishu.baidu.com/")
        cls.save_cookie()
        df = pd.read_json('G:/Innoasset/003_First_Trial_Web_Scraping/cookies.json')
        df['name=value'] = df['name'].apply(lambda x: x+'=') + df['value']
        cls.__driver.close()
        return ";".join(df['name=value'])


class Crawler:
    @staticmethod
    def decrypt(key_val_lst, txt):
        key_val_lst = list(key_val_lst)
        key_len = int(len(key_val_lst)/2)
        key_val_dict = dict(zip(key_val_lst[:key_len], key_val_lst[key_len:]))
        return "".join([key_val_dict[key] for key in txt])


    @staticmethod
    def get_ptbk(uniqid):
        url = 'http://index.baidu.com/Interface/ptbk?uniqid={}'
        ptbk_headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Cookie': COOKIES,
            'DNT': '1',
            'Host': 'index.baidu.com',
            'Pragma': 'no-cache',
            'Proxy-Connection': 'keep-alive',
            'Referer': 'http://index.baidu.com/v2/index.html',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        resp = requests.get(url.format(uniqid), headers=ptbk_headers)
        if resp.status_code != 200:
            logger.error('获取uniqid失败')
            sys.exit(1)
        return resp.json().get('data')


    @classmethod
    def get_index_data(cls, keyword, start='2011-12-27', end='2011-12-27'):
        word_param = f'[[%7B"name":"{keyword}","wordType":1%7D]]'
        url1 = f'http://index.baidu.com/api/SearchApi/index?area=0&word={word_param}&startDate={start}&endDate={end}'
        logger.info(url1)
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Cookie': COOKIES,
            'DNT': '1',
            'Host': 'index.baidu.com',
            'Pragma': 'no-cache',
            'Proxy-Connection': 'keep-alive',
            'Referer': 'http://index.baidu.com/v2/index.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
    
        resp = requests.get(url1, headers=headers)
        if resp.status_code != 200:
            logger.error('获取指数失败')
            sys.exit(1)
    
        data = resp.json().get('data').get('userIndexes')[0]
        uniqid = resp.json().get('data').get('uniqid')
    
        ptbk = cls.get_ptbk(uniqid)
    
        all_data = data.get('all').get('data')
        result = cls.decrypt(ptbk, all_data)
        result = result.split(',')
        return result


class Input:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "keywords", type=str,
            help=("Keywords to search, "
                  "seperate multiple words with commas"))
        parser.add_argument(
            "--start", "-s", type=str,
            help=('''Starting date, any date later than 2011-1-1
                  and (strictly) before today. '''
                  "If not given, take 2011-1-1 by default. "
                  "Used in modify mode only."),
            default='2011-1-1')
        parser.add_argument(
            "--end", "-e", type=str,
            help=('''Ending date, any date later than your starting date
                  and (strictly) before today. '''
                  "If not given, take yesterday by default. "
                  "Used in modify mode only."),
            default=str(datetime.date.today()-datetime.timedelta(days=1)))
        parser.add_argument(
            "--mode", "-m", type=str, choices=['realtime', 'history', 'modify'],
            help=("Select a mode among realtime, history and modify. "
                  """'realtime' updates the file, 'modify'
                  reloads values in selected period """
                  "and 'history' returns the whole set."),
            default='history')
        args = parser.parse_args()
        self.keywords = args.keywords.split(',')
        self.start = args.start
        self.end = args.end
        self.mode = args.mode
        self.title = "_".join(self.keywords)
        
    def is_time_valid(self):
        criteria1 = (parse(self.start).date() >= datetime.date.today())
        criteria2 = (parse(self.start).date() < datetime.date(2011, 1, 1))
        criteria3 = (parse(self.end).date() >= datetime.date.today())
        criteria4 = (parse(self.end).date() < parse(self.start).date())
        return not criteria1 | criteria2 | criteria3 | criteria4
    
    
    # Take part the required time interval, as Baidu will return weekly data for
    # periods longer than one year, instead of daily.
    def take_part(self):
        start = parse(self.start).date()
        end = parse(self.end).date()
        start_0 = start
        data = [start_0]
        while start_0+datetime.timedelta(days=365) < end:
            start_0 = start_0+datetime.timedelta(days=365)
            data = data + [start_0]
            start_0 = start_0+datetime.timedelta(days=1)
            data = data + [start_0]
        data = data+[end]
        time_intervals = np.array(data)
        time_intervals.shape = (int(len(data)/2), 2)
        return time_intervals


    # Convert inputs to final form.
    def inputs_mode_control(self):
        if not self.is_time_valid():
            self.mode = 'history'
            logger.warning('invalid time inputs, modified to history mode')

        one_day = datetime.timedelta(days=1)
        yesterday = datetime.date.today() - one_day
        # If history, request whole dataset.
        if self.mode == 'history':
            inputs = [self.keywords, 
                      '2011-1-1', str(yesterday), self.mode]
        elif self.mode == 'realtime':
            # Try reading the old file and start after its ending date.
            try:
                df_old = pd.read_csv(f"BaiduIndex_{self.title}.csv")
                if parse(df_old.date.iloc[-1]).date() >= yesterday:
                    inputs = [self.keywords, df_old.date.iloc[-1],
                              df_old.date.iloc[-1], 'repetive']
                else:
                    inputs = [self.keywords,
                              str(parse(df_old.date.iloc[-1]).date() + one_day),
                              str(yesterday), self.mode]
            # If not found, switch to history mode.
            except FileNotFoundError:
                logger.warning(('No old version found. '
                       'Create new file with history mode instead.'))
                inputs = [self.keywords, '2011-1-1',
                          str(yesterday), 'history']
        # If modify, set as given.
        elif self.mode == 'modify':
            inputs = [self.keywords, self.start,
                      self.end, self.mode]
        [self.keywords, self.start, self.end, self.mode] = inputs
        logger.info('output results for {} between {} and {}'
                    .format(self.keywords, self.start, self.end))


    # Request data and generate DataFrame.
    def df_generate(self):
        #result = {'date':self.date_list()}
        result = {'date':pd.date_range(self.start,self.end)}
        periods = self.take_part()
    
        for word in self.keywords:
            column = []
            for j in range(len(periods)):
                column = column + Crawler.get_index_data(keyword=word,
                                                 start=periods[j][0],
                                                 end=periods[j][1])
                if j != 0:
                    time.sleep(random.random()*5)
            result.update({word: column})
    
        try:
            df = pd.DataFrame(result)
        except ValueError:
            del result['date'][-1]
            logger.warning('Data for yesterday has not been available yet.')
            try:
                df = pd.DataFrame(result)
            except ValueError:
                del result['date'][-1]
                logger.warning(""""Data for the day before yesterday has also not been
                               available yet, maybe because of weekends.""")
                df = pd.DataFrame(result)
        return df


    def csv_decorator(func):
        
        def wrapper(self):
            df = func(self)
            if df is None:
                return None
            if len(df) > 100:
                df.to_csv(f"BaiduIndex_{self.title}.csv", encoding='utf-8', index=False)
            else:
                df.to_csv(f"BaiduIndex_{self.title}.csv", encoding='utf-8', mode='a',
                          index=False, header=None)
        return wrapper


    # Generate csv file with df in hand according to mode.
    @csv_decorator
    def csv_generate(self):
        df = self.df_generate()
        if self.mode == 'history':
            return df
            #df.to_csv(f"BaiduIndex_{self.title}.csv", encoding='utf-8', index=False)
    
        elif self.mode == 'realtime':
            df_old = pd.read_csv(f"BaiduIndex_{self.title}.csv")
            if len(df.date) > 0:
                return df
                # df.to_csv(f"BaiduIndex_{self.title}.csv", encoding='utf-8', mode='a',
                #           index=False, header=None)
            else:
                logger.warning("So nothing to update.")
    
        elif self.mode == 'modify':
            try:
                df_old = pd.read_csv(f"BaiduIndex_{self.title}.csv")
                standardize = lambda x: parse(x).date().strftime('%Y-%m-%d')
                df_old.date = (df_old.date.apply(standardize))
                df_old.index = copy.deepcopy(df_old.date)
                df.index = copy.deepcopy(df.date)
                df_old.loc[df.index] = df
                df_old.to_csv(f"BaiduIndex_{self.title}.csv",
                              encoding='utf-8', index=False)
            except FileNotFoundError:
                logger.warning("""No old file found.
                               Shall output a new file with data.""")
                df.to_csv(f"BaiduIndex_{self.title}.csv", encoding='utf-8', index=False)


if __name__ == "__main__":
    logger = get_my_logger([['info.log', logging.INFO],
                            ['warning.log', logging.WARNING],
                            ['error.log', logging.ERROR]])
    # KEYWORDS, START, END, MODE = get_inputs()
    inputs = Input()
    inputs.inputs_mode_control()
    if inputs.mode == 'repetive':
        logger.info('Already up to date, no need to update. '
              'If modification is desired, use modify mode.')
    else:
        try:
            COOKIES = Cookies.get_cookies()
            logger.info('Succeeded to get cookies')
            SUCCEED = True
        except Exception as e:
            logger.error('Failed to update cookies, {}'.format(e))
            SUCCEED = False
        
        if SUCCEED:
            inputs.csv_generate()