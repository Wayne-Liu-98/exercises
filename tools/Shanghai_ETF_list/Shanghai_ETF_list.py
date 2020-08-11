# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 15:55:13 2020

@author: 19424
"""
from selenium import webdriver
import time

driver = webdriver.Chrome()
driver.get('https://cn.investing.com/etfs/china-etfs')
time.sleep(10)
codes = []
for i in range(500):
    try:
        codes = codes + [driver.find_element_by_xpath('/html/body/div[6]/section/table/tbody/tr[{}]/td[3]'.format(str(i+1))).text]
    except Exception as e:
        print(e)
        break
codes = [int(x) for x in codes]
print(codes)

        
