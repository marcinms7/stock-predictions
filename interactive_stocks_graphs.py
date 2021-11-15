#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 12 23:15:56 2021

@author: marcinswierczewski
"""

from stocks_api import finnhub_return_close_series, finnhub_news_company

NEWS_AMOUNT = 7
FROM_DATE = '2018-09-01'
STOCKS_LIST = ['MS','PPL','MSFT', 'PYPL', 'MAXR']
df = finnhub_return_close_series(STOCKS_LIST, FROM_DATE)
news = finnhub_news_company(STOCKS_LIST, FROM_DATE)

from datetime import datetime

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import dash_dangerously_set_inner_html

app = dash.Dash(__name__)

app.layout = html.Div([
    
    html.Div([
                html.Div([

                html.Div([
                    html.H5('Marcins Browse of the Followed Stocks'),
                    html.H6('Dashboard inspired by GS style dashboards.', style=dict(color='#7F90AC')),
                    ], className = "nine columns padded" ),

                html.Div([
                    html.H1([html.Span('V.', style=dict(opacity=0.5)), html.Span('0.1')]),
                    html.H6('Daily updates below')
                ], className = "three columns gs-header gs-accent-header padded", style=dict(float='right') ),

            ], className = "row gs-header gs-text-header"),
                
                
                
        
        
    dcc.Dropdown(
        id="ticker",
        options=[{"label": x, "value": x} 
                 for x in df.columns],
        value=df.columns[0],
        clearable=False,),
    dcc.Graph(id="time-series-chart"),
    
    
    
    
    html.Div([
                    html.H6("Latest Company News:", className = "gs-header gs-table-header padded"),
                ], className = "twelve columns" ),
    
    
    
                html.Div([
                    html.P(id='text1')
                ], className = "twelve columns " ),
                
                
                
                    html.Div([
                    html.H6(" ", className = "gs-header gs-table-header padded"),
                ], className = "twelve columns" ),



                ], className = "page" ),
])

@app.callback(
    [Output("time-series-chart", "figure"),
     Output('text1', 'children')],
    [Input("ticker", "value")])
def display_time_series(ticker):
    fig = px.line(df, x=df.index, y=ticker)
    
    news_len = len(news[ticker])
    max_news = min(news_len, NEWS_AMOUNT)
    all_recent_news = ''
    for i in range(max_news):
        headline = news[ticker][i]['headline']
        text = news[ticker][i]['summary']
        news_date = news[ticker][i]['datetime']
        url = news[ticker][i]['url']
        
        all_recent_news += '<b>Date:</b> ' + str(datetime.fromtimestamp(news_date)) + ' <br/> '
        all_recent_news += '<b>HEADLINE</b> :' + str(headline) + ' <br/> '
        all_recent_news += text + ' <br/><br/> '
        # all_recent_news += '<b> URL </b>' + url + ' <br/><br/> '


        
    
    
    return fig, dash_dangerously_set_inner_html.DangerouslySetInnerHTML(all_recent_news)


if __name__ == '__main__':
    app.run_server(debug=True, port=8050, host='0.0.0.0')





















