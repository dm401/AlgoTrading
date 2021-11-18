import requests
import pandas as pd
import ta.momentum
import ta.trend
import datetime

class Market:
    apikey = open("apikey.txt").readline()

    def __init__(self, market, data=None):
        self.market = market
        if not data:
            pd.DataFrame

    def update(self):
        """
        Updates the market with all relevant info and calculates indicators
        """
        # self.getHistorical1Day()
        self.getLivePrice()
        self.getRSI1Day()
        #self.getADX1Day()
        return "Done"

    def getHistorical1Day(self):
        # past 100 *TRADING* days data, actual count may be lower for days not traded like holidays
        i = 100
        print("Getting historical data")
        startDate = datetime.date.today()
        while (i > 0):
            if (startDate.weekday() < 5):
                i -= 1
            startDate = startDate - datetime.timedelta(days=1)
        endDate = datetime.date.today() - datetime.timedelta(days=1)

        url = f"https://api.tiingo.com/tiingo/daily/{self.market}/prices?startDate={startDate}" \
              f"&resampleFreq=daily&token={self.apikey}&endDate={endDate}&format=json"
        x = requests.get(url)
        df = pd.DataFrame(x.json())
        df.drop(columns=df.columns[[4,5,6,7,8,9,10,11,12]], axis=1, inplace=True)
        self.data = df
        return "Done"

    # rn this always appends new data, but sometimes we might only want one piece of data from current day (like in the
    # case of RSI1Day)
    def getLivePrice(self):
        print("Getting live price")
        url = f"https://api.tiingo.com/iex/?tickers={self.market}&token={self.apikey}"
        x = requests.get(url)
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

        #print(self.data)


    def getRSI1Day(self):
        print("Getting RSI")
        df = self.data
        close = df['close'].squeeze()

        rsis = ta.momentum.RSIIndicator(close, 14)
        self.RSI1Day = rsis.rsi().values[-1]


    def getADX1Day(self):
        print("getting ADX")
        df = self.data
        low = df['low'].squeeze()
        high = df['high'].squeeze()
        close = df['close'].squeeze()

        ADXs = ta.trend.ADXIndicator(high, low, close, 14)
        self.ADX = ADXs.adx().values[-1]


    def sell(self):
        return

    def buysell_if_should(self):
        if self.should_buy():
            self.buy()
        if self.should_sell():
            self.sell()

