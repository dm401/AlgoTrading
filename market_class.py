import requests
import pandas as pd
import ta.momentum
import ta.trend
import datetime
import logging

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

        url = f"https://api.tiingo.com/tiingo/daily/{self.market_name}/prices?startDate={startDate}" \
              f"&resampleFreq=daily&token={self.apikey}&endDate={endDate}&format=json"
        x = handle_get_req(url)
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


    def compareToThresholds(self):
        self.score = 0
        if(self.ADX > 25):
            self.score += 1
            logging.debug(self.market_name + " passing ADX\n")
        if(self.RSI1Day < 30):
            self.score += 1
            logging.debug(self.market_name + " passing RSI\n")
        if(self.MACD > 0 and self.MACDYest < 0):
            self.score += 1
            logging.debug(self.market_name + " passing MACD\n")


    def sell(self):
        return

    def buysell_if_should(self):
        if self.should_buy():
            self.buy()
        if self.should_sell():
            self.sell()

def handle_get_req(url, n=0):
    while n < 3:
        try:
            resp = requests.get(url)
            resp.raise_for_status()
        except requests.HTTPError as exc:
            if resp.status_code == 429 and n < 3:
                logging.info("Had to retry url %s as 429, attempt %s", url, n)
                handle_get_req(url, n+1)
        return resp
