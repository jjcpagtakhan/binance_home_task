# coding=utf-8

import time
import requests
import pandas as pd
from prometheus_client import start_http_server, Gauge


class BinanceClient:

    API_URL = 'https://api.binance.com/api'

    def __init__(self):
        self.API_URL = self.API_URL
        self.prom_gauge = Gauge('absolute_delta_value',
                        'Absolute Delta Value of Price Spread', ['symbol'])


    def check_health(self):
        """Test status of Binance API"""
        uri = "/v3/ping"

        r = requests.get(self.API_URL + uri)

        if r.status_code != 200:
            raise Exception("Binance API is unreachable.")

    def get_top_symbols(self, asset, field, output=False):
        """
        Return the top 5 symbols with quote asset BTC
        and the highest volume over the last 24 hours
        in descending order in data frames.
        """
        uri = "/v3/ticker/24hr"

        r = requests.get(self.API_URL + uri)
        df = pd.DataFrame(r.json())
        df = df[['symbol', field]]
        df = df[df.symbol.str.contains(r'(?!$){}$'.format(asset))]
        df[field] = pd.to_numeric(df[field], downcast='float', errors='coerce')
        df = df.sort_values(by=[field], ascending=False).head(5)

        if output:
            print("\n Top Symbols for %s by %s" %  (asset, field))
            print(df)


        return df

    def get_notional_value(self, asset, field, output=False):
        """
        Return the total notional value of the
        200 bids and asks on each symbol's order book
        in dictionary format.

        {'SCBTC_bids': 205.26363838999998,
        'SCBTC_asks': 129.73872442,
        'VETBTC_bids': 217.85985879999998,
        'VETBTC_asks': 82.75020531999999
        }
        """
        uri = "/v3/depth" 

        symbols = self.get_top_symbols(asset, field, output=False)
        notional_list = {}

        for s in symbols['symbol']:
            payload = { 'symbol' : s, 'limit' : 500 }
            r = requests.get(self.API_URL + uri, params=payload)
            for col in ["bids", "asks"]:
                df = pd.DataFrame(data=r.json()[col], columns=["price", "quantity"], dtype=float)
                df = df.sort_values(by=['price'], ascending=False).head(200)
                df['notional'] = df['price'] * df['quantity']
                df['notional'].sum()
                notional_list[s + '_' + col] = df['notional'].sum()

        if output:
            print("\n Total Notional value of %s by %s" %  (asset, field))
            print(notional_list)

        return notional_list

    def get_price_spread(self, asset, field, output=False):
        """
        Return the price spread for each symbols in dictionary format

        {
        'BTCUSDT': 0.010000000002037268,
        'ETHUSDT': 0.07999999999992724,
        'CHZUSDT': 0.00026999999999999247,
        'ALICEUSDT': 0.03170000000000073,
        'BNBUSDT': 0.1057999999999879
        }

        """

        uri = '/v3/ticker/bookTicker'

        symbols = self.get_top_symbols(asset, field)
        spread_list = {}

        for s in symbols['symbol']:
            payload = { 'symbol' : s }
            r = requests.get(self.API_URL + uri, params=payload)
            price_spread = r.json()
            spread_list[s] = float(price_spread['askPrice']) - float(price_spread['bidPrice'])
 
        if output:
            print("\n Price Spread for %s by %s" %  (asset, field))
            print(spread_list)

        return spread_list

    def get_spread_delta(self, asset, field, output=False):

        delta = {}
        old_spread = self.get_price_spread(asset, field)
        time.sleep(10)
        new_spread = self.get_price_spread(asset, field)

        for key in old_spread:
            delta[key] = abs(old_spread[key]-new_spread[key])

        for key in delta:
            self.prom_gauge.labels(key).set(delta[key])

        if output:
            print("\n Absolute Delta for %s" % asset )
            print(delta)



if __name__ == "__main__":
# Start up the server to expose the metrics.
    start_http_server(8080)
    client = BinanceClient()
    client.check_health()

    # To Print Details
    client.get_top_symbols('BTC','volume',True)
    client.get_top_symbols('USDT', 'count', True)
    client.get_notional_value('BTC', 'volume', True)
    client.get_price_spread('USDT', 'count', True)

    while True:
        client.get_spread_delta('USDT', 'count', True)
