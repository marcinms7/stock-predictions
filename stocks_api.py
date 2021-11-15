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
from datetime import datetime
import time

import asyncio

import urllib.request

from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")

from alpha_vantage.timeseries import TimeSeries

# remember to pip install finnhub-python
import finnhub

import plotly
# %matplotlib auto


ALPHA_API_KEY = "C0L2UP54CJFXNEOX"
FINNHUB_CLIENT = finnhub.Client(api_key="c693882ad3ibppargr0g")
# FINNHUB_CLIENT.DEFAULT_TIMEOUT = 300
TODAY = datetime.now().strftime("%Y-%m-%d")

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
        if k == 0:
            dfmain = (alpha_vantage_yearly_time_series(ALPHA_API_KEY,tickers[k])
                      .rename(columns={'1. open': str(v) + '_Price'})[[str(v) + '_Price']])
        else:
            dftemp = (alpha_vantage_yearly_time_series(ALPHA_API_KEY,tickers[k])
                      .rename(columns={'1. open': str(v) + '_Price'})[[str(v) + '_Price']])
            dfmain = dfmain.join(dftemp)
            del dftemp
    return dfmain


    
def finnhub_news_company(tickers, fromdate = "2020-06-01",
                         todate = TODAY):
    news = dict()
    for ticker in tickers:
        news[str(ticker) + '_Price'] = (FINNHUB_CLIENT.company_news(ticker,
                                                         _from=fromdate,
                                                         to=todate))
    return news


def convert_to_unix_date(input_date):
    return int(time.mktime(datetime.strptime
                           (input_date, "%Y-%m-%d").timetuple()))


def finnhub_stock_data(ticker, from_date,
                      to_date = TODAY, freq = 'D'):
    from_date = convert_to_unix_date(from_date)
    to_date = convert_to_unix_date(to_date)
    data = FINNHUB_CLIENT.stock_candles(ticker, freq,
                                        from_date, to_date)
    df = pd.DataFrame(data)
    df.t = df.apply(lambda x: datetime.fromtimestamp(x.t), axis=1)
    return df


def finnhub_return_close_series(tickers, from_date,
                          to_date = TODAY, freq='D'):
    for k, v in enumerate(tickers):
        if k == 0:
            dfmain = (finnhub_stock_data(tickers[k],from_date,
                                         to_date, freq)
                      .rename(columns={'o': str(v) + '_Price',
                                       't':'Date'})
                      .set_index('Date'))
            dfmain = dfmain[[str(v) + '_Price']]
        else:
            dftemp = (finnhub_stock_data(tickers[k],from_date,
                                         to_date, freq)
                      .rename(columns={'o': str(v) + '_Price',
                                       't':'Date'})
                      .set_index('Date'))
            dftemp = dftemp[[str(v) + '_Price']]
            dfmain = dfmain.join(dftemp)
            del dftemp
    return dfmain
        

def plotting_dataframe(dfplot):
    for name in dfplot.columns:
        f, (ax1) = plt.subplots(figsize=(14,5))
        ax1.plot(dfplot.index, dfplot[name])
        ax1.set_xlabel("Date", fontsize=12)
        ax1.set_ylabel("Stock Price")
        ax1.set_title(name + " Close Price History")

























