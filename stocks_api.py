#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 20:31:45 2021

@author: marcinswierczewski
"""
import pandas as pd
import matplotlib.pyplot as plt

from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import time

import asyncio

import urllib.request

from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")

from alpha_vantage.timeseries import TimeSeries

# remember to pip install finnhub-python
import finnhub

ALPHA_API_KEY = "C0L2UP54CJFXNEOX"
FINNHUB_CLIENT = finnhub.Client(api_key="c65f4faad3i9pn79pii0")

# SP_LIST_WEBSITE = "https://datahub.io/core/s-and-p-500-companies"
SP_LIST_WEBSITE = "https://www.liberatedstocktrader.com/sp-500-companies-list-by-sector-market-cap/"

def get_SP_tickers():

    response = requests.get(SP_LIST_WEBSITE)
    soup = BeautifulSoup(response.text)
    
    table = soup.find_all('table')[1]
    rows = table.find_all('tr')
    
    # news = soup.find('div', attrs={'class': 'caas-body'}).text
    
    data = []
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])
    
    result = pd.DataFrame(data, columns=['Sector', 'Ticker', 'Company', 'Market Cap',
                                         'Price/Earning'])
                          
    tickers = result['Ticker'].to_list()
    
    return tickers, result


def alpha_vantage_daily_time_series(alpha_vantage_api_key,
                      ticker_name, data_interval = '30min',
                      details = False):
    #Generate Alpha Vantage time series object
    ts = TimeSeries(key = alpha_vantage_api_key, output_format = 'pandas')
    #outputsize = full extracting data for last 60 days
    data, meta_data = ts.get_intraday(ticker_name, outputsize = 'full', interval= data_interval)
    data['date_time'] = data.index
    if details:
        return data, meta_data
    return data


def alpha_vantage_yearly_time_series(alpha_vantage_api_key,
                       ticker_name, details = False):
    ts = TimeSeries(key = alpha_vantage_api_key, output_format = 'pandas')
    data, meta_data = ts.get_monthly(ticker_name)
    data['date_time'] = data.index
    if details:
        return data, meta_data
    return data




def alpha_vantage_extract(tickers):
    for k,v in enumerate(tickers):
        if k == 1:
            dfmain = (alpha_vantage_yearly_time_series(ALPHA_API_KEY,tickers[k])
                      .rename(columns={'1. open': str(v) + '_Price'})[[str(v) + '_Price']])
        else:
            dftemp = (alpha_vantage_yearly_time_series(ALPHA_API_KEY,tickers[k])
                      .rename(columns={'1. open': str(v) + '_Price'})[[str(v) + '_Price']])
            dfmain = dfmain.join(dftemp)
            del dftemp
    return dfmain


    
def finnhub_news_company(tickers, fromdate = "2020-06-01",
                         todate = "2021-10-10"):
    news = dict()
    for ticker in tickers:
        news[str(ticker)] = (FINNHUB_CLIENT.company_news(ticker,
                                                         _from=fromdate,
                                                         to=todate))
    return news
















                     