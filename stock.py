import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import requests
from matplotlib import rcParams
import config

symbol_string = ""
inputdata = {}


def fetchStockData(symbol):

    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/get-charts"

    querystring = {"symbol": symbol, "interval": "1d",
                   "range": "3mo", "region": "US", "comparisons": "^GDAXI,^FCHI"}
    headers = {
        'x-rapidapi-key': config.KEY,
        'x-rapidapi-host': config.HOST
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)

    if(response.status_code == 200):
        return response.json()
    else:
        return None


def parse_timestamp(inputdata):

    timestamplist = []

    timestamplist.extend(inputdata["chart"]["result"][0]["timestamp"])
    timestamplist.extend(inputdata["chart"]["result"][0]["timestamp"])

    calendertime = []

    for ts in timestamplist:
        dt = datetime.fromtimestamp(ts)
        calendertime.append(dt.strftime("%m/%d/%Y"))

    return calendertime


def parse_values(inputdata):

    valueList = []
    valueList.extend(inputdata["chart"]["result"][0]
                     ["indicators"]["quote"][0]["open"])
    valueList.extend(inputdata["chart"]["result"][0]
                     ["indicators"]["quote"][0]["close"])

    return valueList


def attach_events(inputdata):

    eventlist = []

    for i in range(0, len(inputdata["chart"]["result"][0]["timestamp"])):
        eventlist.append("open")

    for i in range(0, len(inputdata["chart"]["result"][0]["timestamp"])):
        eventlist.append("close")

    return eventlist


def make_graph():
    global symbol_string

    while len(symbol_string) <= 2:
        symbol_string = input("Enter the stock symbol: ")

    retdata = fetchStockData(symbol_string)

    if (None != inputdata):

        inputdata["Timestamp"] = parse_timestamp(retdata)

        inputdata["Values"] = parse_values(retdata)

        inputdata["Events"] = attach_events(retdata)

        df = pd.DataFrame(inputdata)

        sns.set(style="darkgrid")

        rcParams['figure.figsize'] = 13, 5
        rcParams['figure.subplot.bottom'] = 0.2

        ax = sns.lineplot(x="Timestamp", y="Values ($) ", hue="Events", dashes=False, markers=True,
                          data=df, sort=False)

        ax.set_title('Symbol: ' + symbol_string)

        plt.xticks(
            rotation=45,
            horizontalalignment='right',
            fontweight='light',
            fontsize='x-small'
        )

        plt.show()
