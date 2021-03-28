from flask import Flask, render_template, url_for, request, redirect, send_from_directory, flash
import os

# For Stock Visualization Stuff :-)
import datetime as dt
import pandas_datareader as web
import pandas as pd
import plotly.graph_objs as go  # Plotly module to make candlestick graphs
import plotly.io as pio  # Plotly module to convert chart in html

from finvizfinance.quote import finvizfinance
from finvizfinance.news import News

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aehrdxnfhfx'

news_obj = News()
all_news = news_obj.getNews()

titles = all_news['news'].head(20)['Title']
links = all_news['news'].head(20)['Link']
dates = all_news['news'].head(20)['Date']


def visualize(ticker):
    '''
    Function to visualize the stock price data of the provided ticker symbol.
    It uses matplotlib and mpld3 (to convert graph to html)
    RETURNS - An html string
    '''

    start = dt.datetime(2021, 1, 1)
    end = dt.datetime.now()
    # Load Ticker From Entry And Download Data
    data = web.DataReader(ticker, 'yahoo', start, end)

    # Restructure Data Into OHLC Format
    data = data[['Open', 'High', 'Low', 'Close']]

    # Reset Index
    data.reset_index('Date', inplace=True)

    # Make the plotly candlestick graph
    figure = go.Figure(
        data=[go.Candlestick(
            x=data['Date'],
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'])
        ],
        layout=go.Layout(
            height=500,
            template='plotly_dark'
            # Other templates : ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
        )
    )

    figure.update_layout(xaxis_rangeslider_visible=False)
    return pio.to_html(figure)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


# The home page
@app.route('/')
def home():
    return render_template('index.html')

# The requested stock page


@app.route('/<stock_name>')
def get_stock_data(stock_name):
    try:
        graph = visualize(stock_name)
    except:
        flash('Stock not found!', category='error')
        return redirect(url_for('search_page'))

    try:
        stock = finvizfinance(stock_name)
        stock_news = stock.TickerNews()

        titles = stock_news.head(10)['Title']
        links = stock_news.head(10)['Link']
        dates = stock_news.head(10)['Date']

        desc = stock.TickerDescription()
        details = stock.TickerFundament()
    except:
        # flash('Error retrieving stock related details!', category='error')
        desc = 'Description not found!'
        details = {'Company': stock_name, 'Sector': '', 'Industry': ''}
        titles = []
        links = []
        dates = []

        return render_template('stock.html', graph=graph, desc=desc, details=details, titles=titles, links=links, dates=dates)

    return render_template('stock.html', graph=graph, desc=desc, details=details, titles=titles, links=links, dates=dates)


# Search page with news!
@app.route('/search', methods=['GET', 'POST'])
def search_page():
    if request.method == 'POST':
        ticker = request.form.get('stock_name')
        return redirect(url_for('get_stock_data', stock_name=ticker))

    return render_template('search.html', titles=titles, links=links, dates=dates)


# Main function
if __name__ == '__main__':
    app.run(debug=True)
