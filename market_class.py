from numpy import quantile
import requests
import pandas as pd
import ta.momentum
import ta.trend
import datetime
import logging
import time

from consts import base_tingo_url, IG_BASE_URL, IG_DEMO_BASE, IG_PROD_BASE

class Market:
    apikey = open("apikey.txt").readline()

    def __init__(self, market_name, data=None):
        self.market_name = market_name
        if not data:
            pd.DataFrame
        self.score = None
        self.RSI1Day = None
        self.MACD = None
        self.ADX = None
        self.quantity = 0 # Number of shares held

    def write_transaction(self, quantity, price, operation):
        """
        Writes transaction info to file as csv. Should be called by every 
        buy/sell operation
        """
        csv_line = f"{self.market_name},{time.time()},{operation},{quantity},{price}"
        with open(self.market_name, "a") as outfile:
            outfile.write(csv_line)

        # Update the stored quantity
        op = -1 if operation=="sell" else 1
        self.quantity = self.quantity + op*quantity

    def update(self):
        """
        Updates the market with all relevant info and calculates indicators
        """
        # self.getHistorical1Day()
        self.getLivePrice()
        self.getRSI1Day()
        self.getADX1Day()
        self.getMACD1Day()
        self.compareToThresholds()
        return "Done"

    def getHistorical1Day(self):
        # past 100 *TRADING* days data, actual count may be lower for days not traded like holidays
        i = 100
        logging.debug("Getting historical data for %s", self.market_name)
        startDate = datetime.date.today()
        while (i > 0):
            if (startDate.weekday() < 5):
                i -= 1
            startDate = startDate - datetime.timedelta(days=1)
        endDate = datetime.date.today() - datetime.timedelta(days=1)
        url = base_tingo_url.format(f"daily/{self.market_name}/prices")
        params = {
            "startDate": startDate,
            "resampleFreq": "daily",
            "token": self.apikey,
            "endDate": endDate,
            "format": "json"
        }
        x = handle_get_req(url=url, params=params)
        if not x.json():
            logging.debug("Nothing in response...")
        df = pd.DataFrame(x.json())
        df.drop(columns=df.columns[[1,2,3,4,5,9,10,11,12]], axis=1, inplace=True)
        df.rename(columns={'adjClose': 'close', 'adjHigh':'high', 'adjLow': 'low'}, inplace=True)

        self.data = df
        #logging.info(self.data)
        return "Done"

    # rn this always appends new data, but sometimes we might only want one piece of data from current day (like in the
    # case of RSI1Day)
    def getLivePrice(self):
        logging.debug("Getting live price for %s", self.market_name)
        url = f"https://api.tiingo.com/iex/?tickers={self.market_name}&token={self.apikey}"
        x = handle_get_req(url)
        if not x.json():
            logging.debug("Nothing in response...")
        df = pd.DataFrame(x.json())
        df.drop(['ticker', 'bidPrice', 'bidSize', 'lastSaleTimestamp', 'prevClose', 'mid', 'volume',
                 'open', 'quoteTimestamp', 'askPrice', 'askSize', 'lastSize', 'tngoLast'], axis=1, inplace=True)
        df.rename(columns={'last': 'close', 'timestamp': 'date'}, inplace=True)

        # dunno if string matching is cleanest way to do this but seems to work

        currentDataDay = str(df["date"][0])[0:10]
        lastDataDay = str((self.data["date"].iloc[-1])[0:10])

        if currentDataDay == lastDataDay:
            self.data.drop(self.data.tail(1).index, inplace=True)
            self.data = self.data.append(df, ignore_index=True)
        else:
            self.data = self.data.append(df, ignore_index=True)

        #logging.info(self.data)


    def getRSI1Day(self):
        logging.debug("Getting RSI for %s", self.market_name)
        df = self.data
        close = df['close'].squeeze()

        rsis = ta.momentum.RSIIndicator(close, 14)
        self.RSI1Day = rsis.rsi().values[-1]


    def getADX1Day(self):
        logging.debug("Getting ADX for %s", self.market_name)
        df = self.data
        low = df['low'].squeeze()
        high = df['high'].squeeze()
        close = df['close'].squeeze()

        ADXs = ta.trend.ADXIndicator(high, low, close, 14)
        self.ADX = ADXs.adx().values[-1]


    def getMACD1Day(self):
        logging.debug("Getting MACD for %s", self.market_name)
        df = self.data
        close = df['close'].squeeze()

        MACDs = ta.trend.MACD(close)
        self.MACD = MACDs.macd_diff().values[-1]
        self.MACDYest = MACDs.macd_diff().values[-2]
        self.MACDYestYest = MACDs.macd_diff().values[-3]


    def compareToThresholds(self):
        self.score = 0
        if(self.ADX > 25):
            self.score += 1
            logging.debug(self.market_name + " passing ADX\n")
        if(self.RSI1Day < 30):
            self.score += 1
            logging.debug(self.market_name + " passing RSI\n")
        #MACD condition: 3 days with consecutive increase AND today macd hist value > 0
        if(self.MACD > self.MACDYest > self.MACDYestYest and self.MACD > 0):
            self.score += 1
            logging.debug(self.market_name + " passing MACD\n")


    def should_buy(self):
        """
        Checks if we're meeting our conditions for all indicators
        and returns true if so
        """
        return (self.score >= 3)

    def should_sell(self):
        return

    def buy(self, value_per_buy):
        """
        Buys shares
        Link to API docs for buy/sell
        There are various order types, it sounds like we want to make a MARKET
        order, which is a type of immediate order. Pass in Market as the ordertype
        when opening an OTC position
        https://labs.ig.com/rest-trading-api-reference/service-detail?id=608

        POST to endpoint to create a position
        """
        market_info = requests.get(IG_BASE_URL.format(f"/markets/{self.epic}"))
        market_info.raise_for_status()
        market_info = market_info.json().get("snapshot")
        buy_price = market_info.get("offer")

        quantity = value_per_buy/buy_price
        self.quantity = quantity
        url = IG_BASE_URL.format("/positions/otc")
        data = {
            "currencyCode": "GBP", # TODO - check if this needs changing
            "dealReference": f"{self.market}",
            "epic": self.epic, # TODO - need to get this from /markets. EPIC is an IG specific code
            "expiry": "-",
            "orderType": "MARKET",
            "dealSize": round(quantity, 10),
            "direction": "BUY"
        }

        resp = requests.post(url=url, data=data)
        self.deal_ref = resp.json()
        self.write_transaction(self.quantity, buy_price, "buy")
        # TODO - may need to confirm the deal reference???
        return

    def sell(self):
        """
        Sells all shares in the market
        """
        url = IG_BASE_URL.format("/positions/otc")
        data = {
            "currencyCode": "GBP", # TODO - check if this needs changing
            "dealReference": f"{self.market}",
            "epic": self.epic, # TODO - need to get this from /markets. EPIC is an IG specific code
            "expiry": "-",
            "orderType": "MARKET",
            "dealSize": self.quantity,
            "direction": "SELL"
        }

        resp = requests.post(url=url, data=data)
        self.sell_deal_ref = resp.json()
        # self.write_transaction(self.quantity, sell_price, "sell")
        return
    


    def buysell_if_should(self, value_per_buy):
        if self.should_buy():
            self.buy(value_per_buy)
        if self.should_sell():
            self.sell()

def handle_get_req(url, params,n=0):
    while n < 3:
        try:
            resp = requests.get(url, params)
            resp.raise_for_status()
        except requests.HTTPError as exc:
            if resp.status_code == 429 and n < 3:
                logging.info("Had to retry url %s as 429, attempt %s", url, n)
                handle_get_req(url, n+1)
        return resp
