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
        """
        Updates the market with all relevant info and calculates indicators
        """
        # self.getHistorical1Day()
        self.getLivePrice()
        self.getRSI1Day()
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

        url = f"https://api.tiingo.com/iex/{self.market}/prices?startDate={startDate}" \
              f"&resampleFreq=8hour&afterHours=false&forceFill=true&token={self.apikey}&endDate={endDate}"
        x = requests.get(url)
        df = pd.DataFrame(x.json())
        df.drop(columns=df.columns[[2, 3, 4]], axis=1, inplace=True)
        self.data = df
        return "Done"

    # rn this always appends new data, but sometimes we might only want one piece of data from current day (like in the
    # case of RSI1Day)
    def getLivePrice(self):
        print("Getting live price")
        url = f"https://api.tiingo.com/iex/?tickers={self.market}&token={self.apikey}"
        x = requests.get(url)
        df = pd.DataFrame(x.json())
        df.drop(['low', 'ticker', 'bidPrice', 'bidSize', 'lastSaleTimestamp', 'prevClose', 'high', 'mid', 'volume',
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


    def getRSI1Day(self):
        print("Getting RSI")
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

    def buy(self):
        return
    
    def sell(self):
        return

    def buysell_if_should(self):
        if self.should_buy():
            self.buy()
        if self.should_sell():
            self.sell()

