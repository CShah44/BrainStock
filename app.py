from flask import Flask, render_template, url_for, request, redirect, send_from_directory
import os

# For Stock Visualization Stuff :-)
import datetime as dt
import pandas_datareader as web
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
import pandas as pd
import mpld3  # To show matplotlib charts on webpage
from finvizfinance.quote import finvizfinance
from finvizfinance.news import News

app = Flask(__name__)


def visualize(ticker):
    '''
    Function to visualize the stock price data of the provided ticker symbol.
    It uses matplotlib and mpld3 (to convert graph to html)
    RETURNS - An html string
    '''

    start = dt.datetime(2020, 12, 1)
    end = dt.datetime.now()

    # Load Ticker From Entry And Download Data
    data = web.DataReader(ticker, 'yahoo', start, end)

    # Restructure Data Into OHLC Format
    data = data[['Open', 'High', 'Low', 'Close']]

    # Reset Index And Convert Dates Into Numerical Format
    data.reset_index('Date', inplace=True)
    data['Date'] = data['Date'].map(mdates.date2num)

    # Adjust Style Of The Plot
    fig, ax = plt.subplots()
    ax.grid(True)
    ax.set_axisbelow(True)
    ax.set_title(f'{ticker} Share Price')
    # ax.figure.canvas.set_window_title('Stock Price Visualizer')
    # ax.set_facecolor('black')
    # ax.figure.set_facecolor('#121212')
    # ax.tick_params(axis='x', colors='white')
    # ax.tick_params(axis='y', colors='white')
    ax.xaxis_date()

    # plt.figure(figsize=(10, 5))

    # Plot The Candlestick Chart
    candlestick_ohlc(ax, data.values, width=0.5, colorup='#00ff00')
    # mpf.plot(data, type='candle')
    return mpld3.fig_to_html(fig)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/<stock_name>')
def get_stock_data(stock_name):
    graph = visualize(stock_name)
    stock = finvizfinance(stock_name)

    stock_news = stock.TickerNews()

    titles = stock_news.head(10)['Title']
    links = stock_news.head(10)['Link']
    dates = stock_news.head(10)['Date']

    desc = stock.TickerDescription()
    details = stock.TickerFundament()

    return render_template('stock.html', graph=graph, desc=desc, details=details, titles=titles, links=links, dates=dates)


@app.route('/search', methods=['GET', 'POST'])
def search_page():
    if request.method == 'POST':
        ticker = request.form.get('stock_name')
        return redirect(url_for('get_stock_data', stock_name=ticker))

    news_obj = News()
    all_news = news_obj.getNews()

    titles = all_news['news'].head(10)['Title']
    links = all_news['news'].head(10)['Link']
    dates = all_news['news'].head(10)['Date']

    return render_template('search.html', titles=titles, links=links, dates=dates)


if __name__ == '__main__':
    app.run(debug=True)
