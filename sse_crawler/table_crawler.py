# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 11:16:34 2020

@author: 19424
"""

from selenium import webdriver
import pandas as pd
from time import sleep
from log import get_my_logger
import logging
from selenium.webdriver.support.wait import WebDriverWait
import argparse
import os


class TableCrawler:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--url", type=str,
            help=("URL to take tables from."),
            default='http://www.sse.com.cn/assortment/fund/etf/home/')
        parser.add_argument(
            "--file_path", '-f', type=str,
            help=("Path to save csv."),
            default='./output_tables')
        args = parser.parse_args()
        self.url = args.url
        self.path = args.file_path
        # self.url = url
        # self.path = file_path
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(options = chrome_options)
        self.driver.get(self.url)
        self.output_path = "G:\Innoasset\web_scraping"
        self.logger = get_my_logger([['table_info.log', logging.INFO],
                                     ['table_warning.log', logging.WARNING],
                                     ['table_error.log', logging.ERROR]])
        self.df_list = []


    def table_crawler(self):
        WebDriverWait(self.driver,20).until(lambda driver: driver.
                                            find_element_by_xpath('//table/tbody/tr[2]/td[2]'))
        i = 0
        while True:
            results = []
            try:
                tags = self.driver.find_elements_by_xpath('//table')[i].find_elements_by_tag_name('tr')
            except IndexError:
                self.logger.info('{} tables found'.format(str(i)))
                break
            for tag in tags:
                results.append(tag.text.split())
            df = pd.DataFrame(results)
            self.df_list.append(df)
            i += 1


    def save_csv(self):
        folder = os.path.exists(self.path)
        if not folder:
            os.makedirs(self.path)
            self.logger.info('new folder created for saving tables.')
        i = 1
        for df in self.df_list:
            df.to_csv(self.path+'//table{}.csv'.format(str(i)))
            i += 1
        
if __name__ == '__main__':
    CRAWLER = TableCrawler()
    CRAWLER.table_crawler()
    CRAWLER.save_csv()