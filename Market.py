import requests
import pandas as pd
import ta.momentum
import datetime

class Market:
    apikey = open("apikey.txt").readline()

    def __init__(self, market, data=None):
        self.market = market
        
        if not data:
            pd.DataFrame

    def update(self):
        self.getHistorical1Day()
        self.getLivePrice()
        self.getRSI1Day()

    def getHistorical1Day(self):

        # past 100 *TRADING* days data, actual count may be lower for days not traded like holidays
        i = 100
        startDate = datetime.date.today()
        while (i > 0):
            if (startDate.weekday() < 5):
                i -= 1
            startDate = startDate - datetime.timedelta(days=1)
        endDate = datetime.date.today() - datetime.timedelta(days=1)

        url = f"https://api.tiingo.com/iex/{self.market}/prices?startDate={startDate}" \
              f"&resampleFreq=8hour&afterHours=false&forceFill=true&token={self.apikey}&endDate={endDate}"
        x = requests.get(url)

        df = pd.DataFrame(x.json())
        df.drop(columns=df.columns[[2, 3, 4]], axis=1, inplace=True)
        self.data = df

    # rn this always appends new data, but sometimes we might only want one piece of data from current day (like in the
    # case of RSI1Day)
    def getLivePrice(self):

        url = f"https://api.tiingo.com/iex/?tickers={self.market}&token={self.apikey}"
        x = requests.get(url)
        df = pd.DataFrame(x.json())
        df.drop(['low', 'ticker', 'bidPrice', 'bidSize', 'lastSaleTimestamp', 'prevClose', 'high', 'mid', 'volume',
                 'open', 'quoteTimestamp', 'askPrice', 'askSize', 'lastSize', 'tngoLast'], axis=1, inplace=True)
        df.rename(columns={'last': 'close', 'timestamp': 'date'}, inplace=True)

        self.data = self.data.append(df, ignore_index=True)

    def getRSI1Day(self):

        df = self.data

        prices = df['close'].squeeze()

        # check for missing data
        missing = 0
        for x in prices:
            if int(x) == 0:
                missing = 1

        if missing == 0:
            rsis = ta.momentum.RSIIndicator(prices, 14)
            self.RSI1Day = rsis.rsi().values[-1]